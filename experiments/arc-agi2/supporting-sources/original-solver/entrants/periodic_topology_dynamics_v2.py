"""Counterexample-guided periodic and topology programs for Block 14.

V2 is deliberately independent from the promoted v1 entrant.  It adds six
small, replayable mechanisms that v1 could not express: digital-mirror ray
routing, diagonal bead continuation, substrate recolouring inside a marker
support box, sparse-to-dense axis scaffolds, bounded staircase rays, and
Chebyshev halos around non-singleton components.  It also admits a genuinely
multicolour periodic-hole repair.

The v1 clustered-box false activation exposed a more important failure: the
demonstrations did not constrain how a much more fragmented held input should
be partitioned.  Its v2 form therefore serializes demonstration-derived upper
bounds on body and singleton counts and abstains outside that topology.  This
is a score-seeded *uncertainty repair*, not a task-specific answer.

Compilation reads labelled demonstrations and only the ``input`` member of a
test record.  It never reads task identifiers, solutions, scores, result files,
corpus fingerprints, or test outputs.  Enumeration, replay, LOO re-proposal,
counterfactual checks, and ambiguity handling are all finite and fail closed.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from typing import Any, Callable


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]
SCHEMA = "komorebi.pr_lasm.block14.periodic_topology_dynamics_v2_program"
AUTHOR = "Komorebi P."


class Undefined(ValueError):
    """A structural program is absent, ambiguous, or outside its bounds."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_examples: int = 20
    max_total_cells: int = 100_000
    max_programs: int = 512
    max_period: int = 6
    max_steps: int = 8_192
    max_counterfactuals: int = 64
    ambiguity_slack: int = 0
    max_candidates: int = 256

    @classmethod
    def parse(cls, raw: Any) -> "Limits":
        if raw is None:
            return cls()
        if not isinstance(raw, Mapping):
            raise TypeError("limits must be a mapping or None")
        aliases = {
            "candidate_cap": "max_candidates",
            "max_total_candidates": "max_programs",
            "max_replay_calls": None,
            "max_replay_stages": None,
            "max_trace_bytes": None,
            "time_limit": None,
            "time_limit_seconds": None,
        }
        allowed = set(cls.__dataclass_fields__) | set(aliases)
        if set(raw) - allowed:
            raise ValueError("unknown finite limit")
        values: dict[str, int] = {}
        for key, value in raw.items():
            target = aliases.get(key, key)
            if target is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError("finite limits must be integers")
            minimum = 0 if target == "ambiguity_slack" else 1
            if value < minimum:
                raise ValueError("finite limit is below its minimum")
            # Aliases may address the same internal cap.  The stricter cap wins.
            values[target] = min(values.get(target, value), value)
        return cls(**values)


@dataclass(frozen=True, slots=True)
class Proposal:
    family: str
    program: Mapping[str, Any]
    complexity: int
    invariant: str


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _grid(value: Any, max_side: int = 30) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    if not value or len(value) > max_side:
        raise ValueError("invalid grid height")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(
            raw_row, (str, bytes, bytearray)
        ):
            raise TypeError("grid row must be a sequence")
        if width is None:
            width = len(raw_row)
        if width is None or width < 1 or width > max_side or len(raw_row) != width:
            raise ValueError("grid must be nonempty and rectangular")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be integer colors in [0, 9]")
            row.append(int(cell))
        rows.append(tuple(row))
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _sanitize(
    task: Any, limits: Limits
) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise TypeError("task must be a mapping")
    raw_train, raw_test = task["train"], task["test"]
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes, bytearray))
        or len(raw_train) < 2
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes, bytearray))
        or not raw_test
        or len(raw_train) + len(raw_test) > limits.max_examples
    ):
        raise ValueError("invalid task arity")
    total_cells = 0
    train: list[Pair] = []
    for record in raw_train:
        if not isinstance(record, Mapping):
            raise TypeError("training examples must be mappings")
        source = _grid(record["input"], limits.max_side)
        target = _grid(record["output"], limits.max_side)
        total_cells += len(source) * len(source[0]) + len(target) * len(target[0])
        train.append((source, target))
    tests: list[Grid] = []
    for record in raw_test:
        if not isinstance(record, Mapping):
            raise TypeError("test examples must be mappings")
        # The label-blind contract deliberately permits exactly this lookup.
        source = _grid(record["input"], limits.max_side)
        total_cells += len(source) * len(source[0])
        tests.append(source)
    if total_cells > limits.max_total_cells:
        raise ValueError("task cell budget exhausted")
    return tuple(train), tuple(tests)


def _mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise Undefined("empty mode")
    peak = max(counts.values())
    winners = sorted(color for color, count in counts.items() if count == peak)
    if len(winners) != 1:
        raise Undefined("mode is tied")
    return winners[0]


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


def _components(value: Grid, color: int, connectivity: int) -> tuple[frozenset[Cell], ...]:
    if connectivity == 4:
        offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
    elif connectivity == 8:
        offsets = tuple(
            (dr, dc)
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
            if dr or dc
        )
    else:
        raise Undefined("unsupported connectivity")
    unseen = {
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == color
    }
    result: list[frozenset[Cell]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        cells = {root}
        while queue:
            row, column = queue.popleft()
            for dr, dc in offsets:
                other = row + dr, column + dc
                if other in unseen:
                    unseen.remove(other)
                    cells.add(other)
                    queue.append(other)
        result.append(frozenset(cells))
    return tuple(sorted(result, key=lambda cells: (min(cells), len(cells))))


def _d4(value: Grid, operation: str) -> Grid:
    if operation == "identity":
        return value
    if operation == "rot90":
        height, width = _shape(value)
        return tuple(
            tuple(value[height - 1 - row][column] for row in range(height))
            for column in range(width)
        )
    if operation == "rot180":
        return _d4(_d4(value, "rot90"), "rot90")
    if operation == "rot270":
        return _d4(_d4(value, "rot180"), "rot90")
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(
            tuple(value[row][column] for row in range(len(value)))
            for column in range(len(value[0]))
        )
    if operation == "anti_transpose":
        return _d4(_d4(value, "rot180"), "transpose")
    raise Undefined("unknown D4 operation")


def _marker_bbox_substrate(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    marker = int(program["marker"])
    points = [
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == marker
    ]
    if len(points) < 2:
        raise Undefined("marker support is too small")
    top, bottom, left, right = _bbox(points)
    output = [list(row) for row in value]
    changed = False
    for row in range(top, bottom + 1):
        for column in range(left, right + 1):
            if value[row][column] == source:
                output[row][column] = paint
                changed = True
    if not changed:
        raise Undefined("marker box contains no substrate")
    return tuple(tuple(row) for row in output)


def _component_halo(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    object_color = int(program["object_color"])
    radius = int(program["radius"])
    if radius != 1:
        raise Undefined("halo radius is outside the grammar")
    bodies = [cells for cells in _components(value, object_color, 4) if len(cells) > 1]
    if not bodies:
        raise Undefined("no nontrivial foreground component")
    height, width = _shape(value)
    output = [list(row) for row in value]
    changed = False
    for cells in bodies:
        for row, column in cells:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    other_row, other_column = row + dr, column + dc
                    if (
                        0 <= other_row < height
                        and 0 <= other_column < width
                        and value[other_row][other_column] == source
                    ):
                        output[other_row][other_column] = paint
                        changed = True
    if not changed:
        raise Undefined("component halo makes no change")
    return tuple(tuple(row) for row in output)


def _diagonal_bead_complement(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    object_color = int(program["object_color"])
    components = _components(value, object_color, 8)
    if not components:
        raise Undefined("no bead components")
    height, width = _shape(value)
    output = [list(row) for row in value]
    changed = False
    for cells in components:
        bead_float = math.isqrt(len(cells) // 2) if len(cells) % 2 == 0 else 0
        bead = bead_float
        if bead < 1 or 2 * bead * bead != len(cells):
            raise Undefined("component is not two equal square beads")
        top, bottom, left, right = _bbox(cells)
        if bottom - top + 1 != 2 * bead or right - left + 1 != 2 * bead:
            raise Undefined("bead component has the wrong envelope")
        top_left = {
            (row, column)
            for row in range(top, top + bead)
            for column in range(left, left + bead)
        }
        top_right = {
            (row, column)
            for row in range(top, top + bead)
            for column in range(right - bead + 1, right + 1)
        }
        bottom_left = {
            (row, column)
            for row in range(bottom - bead + 1, bottom + 1)
            for column in range(left, left + bead)
        }
        bottom_right = {
            (row, column)
            for row in range(bottom - bead + 1, bottom + 1)
            for column in range(right - bead + 1, right + 1)
        }
        if cells == frozenset(top_left | bottom_right):
            origins = ((top - bead, right + 1), (bottom + 1, left - bead))
        elif cells == frozenset(top_right | bottom_left):
            origins = ((top - bead, left - bead), (bottom + 1, right + 1))
        else:
            raise Undefined("beads are not diagonally opposed")
        visible = 0
        for origin_row, origin_column in origins:
            for dr in range(bead):
                for dc in range(bead):
                    row, column = origin_row + dr, origin_column + dc
                    if not (0 <= row < height and 0 <= column < width):
                        continue
                    visible += 1
                    if value[row][column] != source:
                        raise Undefined("complementary bead collides with foreground")
                    output[row][column] = paint
                    changed = True
        if not visible:
            raise Undefined("both complementary beads are outside the canvas")
    if not changed:
        raise Undefined("bead continuation makes no change")
    return tuple(tuple(row) for row in output)


def _dense_axis_scaffold(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    object_color = int(program["object_color"])
    points = [
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == object_color
    ]
    if len(points) < 4:
        raise Undefined("scaffold evidence is too sparse")
    top, bottom, left, right = _bbox(points)
    height, width = bottom - top + 1, right - left + 1
    if height < 3 or width < 3:
        raise Undefined("scaffold envelope is degenerate")
    selected_rows = {top, bottom}
    selected_columns = {left, right}
    selected_rows.update(
        row
        for row in range(top + 1, bottom)
        if 2
        * sum(value[row][column] == object_color for column in range(left, right + 1))
        > width
    )
    selected_columns.update(
        column
        for column in range(left + 1, right)
        if 2
        * sum(value[row][column] == object_color for row in range(top, bottom + 1))
        > height
    )
    cells = {
        (row, column)
        for row in selected_rows
        for column in range(left, right + 1)
    } | {
        (row, column)
        for column in selected_columns
        for row in range(top, bottom + 1)
    }
    output = [list(row) for row in value]
    changed = False
    for row, column in cells:
        if value[row][column] == source:
            output[row][column] = paint
            changed = True
        elif value[row][column] != object_color:
            raise Undefined("scaffold crosses a foreign color")
    if not changed:
        raise Undefined("scaffold is already complete")
    return tuple(tuple(row) for row in output)


def _turn(direction: Cell, side: str) -> Cell:
    row, column = direction
    if side == "left":
        return -column, row
    if side == "right":
        return column, -row
    raise Undefined("unknown turn")


def _mirror_ray(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    path_color = int(program["path_color"])
    left_color = int(program["left_color"])
    right_color = int(program["right_color"])
    height, width = _shape(value)
    starts: list[tuple[Cell, Cell]] = []
    for row in range(height):
        for column in range(width):
            if value[row][column] != path_color:
                continue
            if row == 0:
                starts.append(((row, column), (1, 0)))
            if row == height - 1:
                starts.append(((row, column), (-1, 0)))
            if column == 0:
                starts.append(((row, column), (0, 1)))
            if column == width - 1:
                starts.append(((row, column), (0, -1)))
    if len(starts) != 1:
        raise Undefined("ray requires one non-corner boundary source")
    if sum(cell == path_color for row in value for cell in row) != 1:
        raise Undefined("ray source color is not unique")
    all_reflectors = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] in (left_color, right_color)
    }
    if not all_reflectors:
        raise Undefined("ray has no reflectors")
    output = [list(row) for row in value]
    position, direction = starts[0]
    visited: set[tuple[Cell, Cell]] = set()
    touched: set[Cell] = set()
    changed = False
    for _ in range(height * width * 8):
        state = position, direction
        if state in visited:
            raise Undefined("ray entered a cycle")
        visited.add(state)
        next_row = position[0] + direction[0]
        next_column = position[1] + direction[1]
        if not (0 <= next_row < height and 0 <= next_column < width):
            if touched != all_reflectors or not changed:
                raise Undefined("ray did not consume the reflector set")
            return tuple(tuple(row) for row in output)
        color = value[next_row][next_column]
        if color == background:
            output[next_row][next_column] = path_color
            position = next_row, next_column
            changed = True
        elif color == left_color:
            touched.add((next_row, next_column))
            direction = _turn(direction, "left")
        elif color == right_color:
            touched.add((next_row, next_column))
            direction = _turn(direction, "right")
        else:
            raise Undefined("ray met an unsupported obstacle")
    raise Undefined("ray step bound exhausted")


def _staircase_ray(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    seed_color = int(program["seed_color"])
    segment = int(program["segment_length"])
    diagonal = str(program["diagonal"])
    if not 1 <= segment <= 4 or diagonal not in {"ne_sw", "nw_se"}:
        raise Undefined("invalid staircase program")
    seeds = [
        (row, column)
        for row in range(len(value))
        for column in range(len(value[0]))
        if value[row][column] == seed_color
    ]
    if len(seeds) != 1:
        raise Undefined("staircase requires one seed")
    height, width = _shape(value)
    horizontal = 1 if diagonal == "ne_sw" else -1
    output = [list(row) for row in value]
    changed = False
    for vertical, sideways in ((-1, horizontal), (1, -horizontal)):
        row, column = seeds[0]
        directions = ((vertical, 0), (0, sideways))
        phase = 0
        while True:
            dr, dc = directions[phase % 2]
            exited = False
            for _ in range(segment):
                next_row, next_column = row + dr, column + dc
                if not (0 <= next_row < height and 0 <= next_column < width):
                    exited = True
                    break
                if value[next_row][next_column] != source:
                    raise Undefined("staircase collides with foreground")
                row, column = next_row, next_column
                output[row][column] = paint
                changed = True
            if exited:
                break
            phase += 1
            if phase > height * width * 2:
                raise Undefined("staircase step bound exhausted")
    if not changed:
        raise Undefined("staircase makes no change")
    return tuple(tuple(row) for row in output)


def _periodic_hole_repair(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    row_period = int(program["row_period"])
    column_period = int(program["column_period"])
    if not 1 <= row_period <= 6 or not 1 <= column_period <= 6:
        raise Undefined("period outside the grammar")
    observations: list[list[list[int]]] = [
        [[] for _ in range(column_period)] for _ in range(row_period)
    ]
    for row in range(len(value)):
        for column in range(len(value[0])):
            color = value[row][column]
            if color != source:
                observations[row % row_period][column % column_period].append(color)
    template = [[source] * column_period for _ in range(row_period)]
    for row in range(row_period):
        for column in range(column_period):
            visible = observations[row][column]
            if visible:
                if len(set(visible)) != 1:
                    raise Undefined("periodic residue has conflicting observations")
                template[row][column] = visible[0]
    output = [list(row) for row in value]
    changed = False
    for row in range(len(value)):
        for column in range(len(value[0])):
            expected = template[row % row_period][column % column_period]
            if value[row][column] == source and expected != source:
                output[row][column] = expected
                changed = True
    if not changed:
        raise Undefined("periodic repair makes no change")
    return tuple(tuple(row) for row in output)


def _cluster_signature(value: Grid, object_color: int) -> tuple[int, int]:
    components = _components(value, object_color, 4)
    return sum(len(cells) > 1 for cells in components), sum(len(cells) == 1 for cells in components)


def _guarded_cluster_boxes(value: Grid, program: Mapping[str, Any]) -> Grid:
    source = int(program["source"])
    paint = int(program["paint"])
    object_color = int(program["object_color"])
    body_cap = int(program["maximum_body_components"])
    singleton_cap = int(program["maximum_singletons"])
    bodies_count, singleton_count = _cluster_signature(value, object_color)
    if bodies_count > body_cap or singleton_count > singleton_cap:
        raise Undefined("held topology is outside the demonstration envelope")
    components = _components(value, object_color, 4)
    bodies = [set(cells) for cells in components if len(cells) > 1]
    markers = [next(iter(cells)) for cells in components if len(cells) == 1]
    if not bodies or not markers:
        raise Undefined("body-plus-singleton topology is absent")
    for marker in markers:
        distances = [
            Fraction(
                (marker[0] * len(body) - sum(row for row, _ in body)) ** 2
                + (marker[1] * len(body) - sum(column for _, column in body)) ** 2,
                len(body) ** 2,
            )
            for body in bodies
        ]
        minimum = min(distances)
        if distances.count(minimum) != 1:
            raise Undefined("singleton attachment is ambiguous")
        bodies[distances.index(minimum)].add(marker)
    output = [list(row) for row in value]
    changed = False
    for body in bodies:
        top, bottom, left, right = _bbox(body)
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                if value[row][column] == source:
                    output[row][column] = paint
                    changed = True
    if not changed:
        raise Undefined("cluster boxes make no change")
    return tuple(tuple(row) for row in output)


_EXECUTORS: dict[str, Callable[[Grid, Mapping[str, Any]], Grid]] = {
    "marker_bbox_substrate_recolor": _marker_bbox_substrate,
    "nontrivial_component_chebyshev_halo": _component_halo,
    "diagonal_bead_complement": _diagonal_bead_complement,
    "dense_axis_scaffold_completion": _dense_axis_scaffold,
    "digital_mirror_ray_router": _mirror_ray,
    "bidirectional_staircase_ray": _staircase_ray,
    "periodic_multicolor_hole_repair": _periodic_hole_repair,
    "guarded_clustered_bbox_completion": _guarded_cluster_boxes,
}


def execute_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Execute one finite serialized program."""

    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    executor = _EXECUTORS.get(str(program.get("operator")))
    if executor is None:
        raise Undefined("unknown operator")
    return _plain(executor(_grid(grid), program))


def replay_program(program: Mapping[str, Any], grid: Any) -> list[list[int]]:
    """Tournament replay hook; the input and program are never mutated."""

    return execute_program(program, grid)


def _program(operator: str, **parameters: Any) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "operator": operator,
        "root_scope": "immutable_input",
        **parameters,
    }


def _changed_pairs(train: Sequence[Pair]) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(
            {
                (before, after)
                for source, target in train
                for source_row, target_row in zip(source, target)
                for before, after in zip(source_row, target_row)
                if before != after
            }
        )
    )


def _same_shape_nonidentity(train: Sequence[Pair]) -> bool:
    return all(_shape(source) == _shape(target) and source != target for source, target in train)


def _exact(program: Mapping[str, Any], train: Sequence[Pair]) -> bool:
    try:
        return all(_grid(execute_program(program, source)) == target for source, target in train)
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return False


def _enumerate(train: Sequence[Pair], limits: Limits) -> tuple[Proposal, ...]:
    if not _same_shape_nonidentity(train):
        return ()
    proposals: dict[str, Proposal] = {}
    attempts = 0

    def add(family: str, program: dict[str, Any], complexity: int, invariant: str) -> None:
        nonlocal attempts
        attempts += 1
        if attempts > limits.max_programs:
            raise Undefined("program enumeration bound exhausted")
        key = _canonical(program)
        if key not in proposals and _exact(program, train):
            proposals[key] = Proposal(family, program, complexity, invariant)

    pairs = _changed_pairs(train)
    input_union = sorted(
        {
            color
            for source, _ in train
            for row in source
            for color in row
        }
    )
    if len(pairs) == 1:
        source, paint = pairs[0]
        other_colors = [color for color in input_union if color not in {source, paint}]
        for object_color in other_colors:
            add(
                "topology.marker_bbox_substrate",
                _program(
                    "marker_bbox_substrate_recolor",
                    source=source,
                    paint=paint,
                    marker=object_color,
                    support="global_marker_bbox",
                ),
                8,
                "d4",
            )
            add(
                "topology.component_halo",
                _program(
                    "nontrivial_component_chebyshev_halo",
                    source=source,
                    paint=paint,
                    object_color=object_color,
                    connectivity=4,
                    radius=1,
                ),
                7,
                "d4",
            )
            add(
                "topology.diagonal_bead_complement",
                _program(
                    "diagonal_bead_complement",
                    source=source,
                    paint=paint,
                    object_color=object_color,
                    component_connectivity=8,
                    clipping="canvas_intersection",
                ),
                8,
                "d4",
            )
            add(
                "topology.dense_axis_scaffold",
                _program(
                    "dense_axis_scaffold_completion",
                    source=source,
                    paint=paint,
                    object_color=object_color,
                    envelope="global_bbox",
                    internal_axis_threshold="strict_majority",
                ),
                10,
                "d4",
            )
            add(
                "topology.staircase_ray",
                _program(
                    "bidirectional_staircase_ray",
                    source=source,
                    paint=paint,
                    seed_color=object_color,
                    diagonal="ne_sw",
                    segment_length=2,
                ),
                9,
                "rot180",
            )
            add(
                "topology.staircase_ray",
                _program(
                    "bidirectional_staircase_ray",
                    source=source,
                    paint=paint,
                    seed_color=object_color,
                    diagonal="nw_se",
                    segment_length=2,
                ),
                9,
                "rot180",
            )

            signatures = [_cluster_signature(grid, object_color) for grid, _ in train]
            body_cap = max(body_count for body_count, _ in signatures)
            singleton_cap = max(singleton_count for _, singleton_count in signatures)
            add(
                "topology.guarded_cluster_boxes",
                _program(
                    "guarded_clustered_bbox_completion",
                    source=source,
                    paint=paint,
                    object_color=object_color,
                    connectivity=4,
                    singleton_attachment="unique_nearest_body_centroid",
                    maximum_body_components=body_cap,
                    maximum_singletons=singleton_cap,
                    novelty_policy="abstain_above_demonstration_envelope",
                ),
                12,
                "d4",
            )

        if source != paint and len(other_colors) >= 2:
            for left_color in other_colors:
                for right_color in other_colors:
                    if left_color == right_color:
                        continue
                    add(
                        "topology.digital_mirror_ray",
                        _program(
                            "digital_mirror_ray_router",
                            background=source,
                            path_color=paint,
                            left_color=left_color,
                            right_color=right_color,
                            reflector_policy="turn_before_preserved_marker",
                            terminal_policy="canvas_boundary",
                            reflector_coverage="all",
                        ),
                        8,
                        "c4",
                    )

    changed_sources = {before for before, _ in pairs}
    if len(changed_sources) == 1:
        missing = next(iter(changed_sources))
        minimum_height = min(len(source) for source, _ in train)
        minimum_width = min(len(source[0]) for source, _ in train)
        for row_period in range(1, min(limits.max_period, minimum_height) + 1):
            for column_period in range(1, min(limits.max_period, minimum_width) + 1):
                add(
                    "periodic.multicolor_hole_repair",
                    _program(
                        "periodic_multicolor_hole_repair",
                        source=missing,
                        row_period=row_period,
                        column_period=column_period,
                        residue_policy="unique_visible_non_source",
                    ),
                    12 + row_period + column_period,
                    "periodic_d4",
                )
    return tuple(
        sorted(proposals.values(), key=lambda proposal: (proposal.complexity, _canonical(proposal.program)))
    )


def _transform_program(program: Mapping[str, Any], operation: str) -> Mapping[str, Any]:
    transformed = dict(program)
    if program.get("operator") == "periodic_multicolor_hole_repair" and operation in {
        "rot90",
        "rot270",
        "transpose",
        "anti_transpose",
    }:
        transformed["row_period"], transformed["column_period"] = (
            int(program["column_period"]),
            int(program["row_period"]),
        )
    return transformed


def _counterfactual(
    proposal: Proposal, train: Sequence[Pair], limits: Limits
) -> tuple[tuple[str, ...], int] | None:
    operations = {
        "d4": ("rot90", "flip_h"),
        "c4": ("rot90", "rot180"),
        "rot180": ("rot180",),
        "periodic_d4": ("rot90", "flip_h"),
    }.get(proposal.invariant)
    if operations is None:
        return None
    probes = 0
    try:
        for source, target in train:
            for operation in operations:
                if probes >= limits.max_counterfactuals:
                    raise Undefined("counterfactual bound exhausted")
                transformed_source = _d4(source, operation)
                transformed_target = _d4(target, operation)
                transformed_program = _transform_program(proposal.program, operation)
                if _grid(execute_program(transformed_program, transformed_source)) != transformed_target:
                    return None
                probes += 1
        name = {
            "d4": "d4_covariance",
            "c4": "rotation_covariance",
            "rot180": "half_turn_covariance",
            "periodic_d4": "period_lattice_d4_covariance",
        }[proposal.invariant]
        return (name,), probes
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return None


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
            if _grid(execute_program(proposal.program, train[held_index][0])) != train[held_index][1]:
                return False
        except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
            return False
    return True


def _behavior_hash(outputs: Sequence[Grid]) -> str:
    return hashlib.sha256(
        _canonical([_plain(output) for output in outputs]).encode("utf-8")
    ).hexdigest()


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return one uniquely predictive executable capsule, or abstain."""

    try:
        bounds = Limits.parse(limits)
        train, tests = _sanitize(task, bounds)
        proposals = _enumerate(train, bounds)
        if not proposals:
            return []
        guarded: list[tuple[Proposal, tuple[Grid, ...], tuple[str, ...], int]] = []
        minimum = proposals[0].complexity
        near = [p for p in proposals if p.complexity <= minimum + bounds.ambiguity_slack]
        for proposal in near:
            if not _loo_exact(proposal, train, bounds):
                continue
            certificate = _counterfactual(proposal, train, bounds)
            if certificate is None:
                continue
            try:
                predictions = tuple(
                    _grid(execute_program(proposal.program, test)) for test in tests
                )
            except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
                continue
            if all(prediction == test for prediction, test in zip(predictions, tests)):
                continue
            guarded.append((proposal, predictions, certificate[0], certificate[1]))
        if not guarded:
            return []

        minimum_guarded = min(item[0].complexity for item in guarded)
        winners = [item for item in guarded if item[0].complexity == minimum_guarded]
        behaviors = {_behavior_hash(item[1]) for item in winners}
        # Both program ambiguity and behavioral ambiguity are explicit abstentions.
        if len(winners) != 1 or len(behaviors) != 1:
            return []
        proposal, predictions, invariants, probe_count = winners[0]
        repair = proposal.program.get("operator") == "guarded_clustered_bbox_completion"
        candidate = {
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
                "counterfactual_families": list(invariants),
                "counterfactual_probe_count": probe_count,
                "bounded_program_enumeration": True,
                "program_attempt_cap": bounds.max_programs,
                "minimum_serialized_program_unique": True,
                "near_mdl_program_count": len(near),
                "ambiguity_abstention": True,
                "test_access": "input_key_only",
                "task_identity_access": "none",
                "score_seeded_uncertainty_repair": repair,
                "behavior_hash": _behavior_hash(predictions),
            },
        }
        return [candidate][: bounds.max_candidates]
    except (Undefined, KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return []


__all__ = [
    "Limits",
    "compile_task",
    "execute_program",
    "replay_program",
]
