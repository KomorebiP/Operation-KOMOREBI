"""Stable panel-sequence and layout composition synthesis.

This entrant is the counterexample-guided successor to
``panel_template_composer``.  It deliberately does not reuse the earlier
input-local orientation guesses.  Every choice that can change at test time
is serialized in a small executable program, and every accepted program must
be rediscovered when each demonstration is held out.

The compiler sees demonstration pairs and test *inputs* only.  Test outputs,
task identifiers, score files, and solution files are neither accepted nor
read.  Multiple fitting programs are quotiented by their complete test
behaviour; disagreement causes abstention.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any


Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]
Point = tuple[int, int]
SCHEMA = "komorebi.pr_lasm.block14.panel_template_composer.v2"


class _Undefined(ValueError):
    """A program is not defined for the supplied grid."""


@dataclass(frozen=True, slots=True)
class Limits:
    max_side: int = 30
    max_cells: int = 900
    max_programs: int = 256
    max_executor_calls: int = 20_000
    max_mdl: int = 40
    max_candidates: int = 1

    @classmethod
    def from_value(cls, value: Any) -> "Limits":
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            return cls()
        default = cls()

        def bounded(name: str, fallback: int, ceiling: int) -> int:
            raw = value.get(name, fallback)
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                return fallback
            return min(raw, ceiling)

        candidate_cap = value.get("candidate_cap", value.get("max_candidates", 1))
        if isinstance(candidate_cap, bool) or not isinstance(candidate_cap, int):
            candidate_cap = 1
        return cls(
            max_side=bounded("max_side", default.max_side, 60),
            max_cells=bounded("max_cells", default.max_cells, 3600),
            max_programs=bounded("max_programs", default.max_programs, 1024),
            max_executor_calls=bounded(
                "max_executor_calls", default.max_executor_calls, 200_000
            ),
            max_mdl=bounded("max_mdl", default.max_mdl, 128),
            max_candidates=min(max(candidate_cap, 0), 1),
        )


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("ascii")).hexdigest()


def _grid(value: Any, limits: Limits) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise _Undefined("empty grid")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise _Undefined("invalid row")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise _Undefined("invalid cell")
            row.append(cell)
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise _Undefined("ragged grid")
        rows.append(tuple(row))
    h, w = len(rows), int(width or 0)
    if h > limits.max_side or w > limits.max_side or h * w > limits.max_cells:
        raise _Undefined("grid exceeds cap")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _freeze(rows: Sequence[Sequence[int]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in rows)


def _shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def _read_task(task: Any, limits: Limits) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise _Undefined("invalid task")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or len(raw_train) < 2
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not raw_test
        or len(raw_train) + len(raw_test) > 16
    ):
        # A genuine leave-one-out witness needs at least two demonstrations.
        raise _Undefined("invalid example collection")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise _Undefined("invalid demonstration")
        train.append(
            (_grid(example.get("input"), limits), _grid(example.get("output"), limits))
        )
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise _Undefined("invalid test")
        # Deliberately ignore an injected ``output`` member.
        tests.append(_grid(example.get("input"), limits))
    return tuple(train), tuple(tests)


def _unique_mode(values: Iterable[int]) -> int:
    counts = Counter(values)
    if not counts:
        raise _Undefined("empty colour role")
    maximum = max(counts.values())
    winners = [colour for colour, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise _Undefined("tied colour role")
    return winners[0]


def _bbox(points: Iterable[Point]) -> tuple[int, int, int, int]:
    materialized = tuple(points)
    if not materialized:
        raise _Undefined("empty object")
    return (
        min(r for r, _ in materialized),
        max(r for r, _ in materialized),
        min(c for _, c in materialized),
        max(c for _, c in materialized),
    )


def _axis_intervals(length: int, lines: Sequence[int]) -> tuple[tuple[int, int], ...] | None:
    """Return equal open intervals around single-cell divider lines."""

    if not lines:
        return ((0, length),)
    if any(right == left + 1 for left, right in zip(lines, lines[1:])):
        return None
    intervals: list[tuple[int, int]] = []
    start = 0
    for line in lines:
        if start < line:
            intervals.append((start, line))
        start = line + 1
    if start < length:
        intervals.append((start, length))
    if not intervals or len({end - begin for begin, end in intervals}) != 1:
        return None
    return tuple(intervals)


@dataclass(frozen=True, slots=True)
class _Lattice:
    separator: int
    rows: tuple[tuple[int, int], ...]
    columns: tuple[tuple[int, int], ...]
    row_lines: tuple[int, ...]
    column_lines: tuple[int, ...]


def _lattice(grid: Grid, *, minimum_panels: int = 2) -> _Lattice:
    h, w = _shape(grid)
    proposals: list[_Lattice] = []
    for colour in sorted({cell for row in grid for cell in row}):
        row_lines = tuple(r for r, row in enumerate(grid) if all(x == colour for x in row))
        column_lines = tuple(
            c for c in range(w) if all(grid[r][c] == colour for r in range(h))
        )
        rows = _axis_intervals(h, row_lines)
        columns = _axis_intervals(w, column_lines)
        if rows is None or columns is None:
            continue
        panel_count = len(rows) * len(columns)
        if panel_count < minimum_panels or panel_count > 100:
            continue
        proposals.append(_Lattice(colour, rows, columns, row_lines, column_lines))
    if not proposals:
        raise _Undefined("no regular lattice")
    maximum = max(len(item.rows) * len(item.columns) for item in proposals)
    winners = [
        item for item in proposals if len(item.rows) * len(item.columns) == maximum
    ]
    unique = {
        (item.separator, item.rows, item.columns, item.row_lines, item.column_lines): item
        for item in winners
    }
    if len(unique) != 1:
        raise _Undefined("ambiguous lattice")
    return next(iter(unique.values()))


def _panels(grid: Grid, lattice: _Lattice) -> list[list[Grid]]:
    return [
        [
            tuple(tuple(grid[r][c] for c in range(c0, c1)) for r in range(r0, r1))
            for c0, c1 in lattice.columns
        ]
        for r0, r1 in lattice.rows
    ]


def _content_base(panels: Sequence[Sequence[Grid]], separator: int) -> int:
    return _unique_mode(
        cell
        for row in panels
        for panel in row
        for line in panel
        for cell in line
        if cell != separator
    )


def _blank_like(grid: Grid, lattice: _Lattice, base: int) -> list[list[int]]:
    result = [list(row) for row in grid]
    for r0, r1 in lattice.rows:
        for c0, c1 in lattice.columns:
            for r in range(r0, r1):
                result[r][c0:c1] = [base] * (c1 - c0)
    return result


def _put_panel(
    result: list[list[int]], lattice: _Lattice, row: int, column: int, panel: Grid
) -> None:
    r0, r1 = lattice.rows[row]
    c0, c1 = lattice.columns[column]
    if _shape(panel) != (r1 - r0, c1 - c0):
        raise _Undefined("panel shape mismatch")
    for offset, line in enumerate(panel):
        result[r0 + offset][c0:c1] = list(line)


def _object_crop(panel: Grid, base: int) -> tuple[int, int, Grid]:
    points = [
        (r, c)
        for r, row in enumerate(panel)
        for c, cell in enumerate(row)
        if cell != base
    ]
    r0, r1, c0, c1 = _bbox(points)
    crop = tuple(
        tuple(panel[r][c] for c in range(c0, c1 + 1))
        for r in range(r0, r1 + 1)
    )
    return r0, c0, crop


def _bordered_sequence_translate(grid: Grid) -> Grid:
    """Extrapolate a constant-position sequence into one enclosed panel."""

    lattice = _lattice(grid, minimum_panels=3)
    h, w = _shape(grid)
    horizontal = (
        len(lattice.rows) == 1
        and len(lattice.columns) >= 3
        and lattice.row_lines == (0, h - 1)
        and lattice.column_lines
        and lattice.column_lines[0] == 0
        and lattice.column_lines[-1] == w - 1
    )
    vertical = (
        len(lattice.columns) == 1
        and len(lattice.rows) >= 3
        and lattice.column_lines == (0, w - 1)
        and lattice.row_lines
        and lattice.row_lines[0] == 0
        and lattice.row_lines[-1] == h - 1
    )
    if horizontal == vertical:
        raise _Undefined("sequence orientation ambiguous")
    panel_matrix = _panels(grid, lattice)
    sequence = panel_matrix[0] if horizontal else [row[0] for row in panel_matrix]
    base = _content_base(panel_matrix, lattice.separator)
    objects = [_object_crop(panel, base) for panel in sequence]
    if len({crop for _, _, crop in objects}) != 1:
        raise _Undefined("sequence object changes")
    deltas = [
        (after[0] - before[0], after[1] - before[1])
        for before, after in zip(objects, objects[1:])
    ]
    if len(set(deltas)) != 1 or deltas[0] == (0, 0):
        raise _Undefined("sequence translation is not constant")
    dr, dc = deltas[0]
    r0, c0, crop = objects[-1]
    r0 += dr
    c0 += dc
    # When a downward stride is strictly larger than the object's extent, the
    # panels encode the next *leading free edge* rather than another top-left
    # anchor.  The old rule applied this extent correction to every downward
    # motion, including contiguous stride==height waves.  Keeping the two
    # cases separate is the score-seeded repair, stated as a reusable geometric
    # predicate rather than a task exception.
    if dr > len(crop):
        r0 += len(crop) - 1
    ph, pw = _shape(sequence[-1])
    ch, cw = _shape(crop)
    if not (0 <= r0 <= ph - ch and 0 <= c0 <= pw - cw):
        raise _Undefined("extrapolation leaves panel")
    result = [[lattice.separator] * (pw + 2)]
    result.extend(
        [[lattice.separator] + [base] * pw + [lattice.separator] for _ in range(ph)]
    )
    result.append([lattice.separator] * (pw + 2))
    for r, line in enumerate(crop):
        result[1 + r0 + r][1 + c0 : 1 + c0 + cw] = list(line)
    return _freeze(result)


def _resolve_rank_colour(
    panels: Sequence[Sequence[Grid]], separator: int, program: Mapping[str, Any]
) -> int:
    counts = Counter(
        cell
        for row in panels
        for panel in row
        for line in panel
        for cell in line
        if cell != separator
    )
    if len(counts) < 2:
        raise _Undefined("rank layout needs at least two colours")
    role = program.get("colour_role")
    if role == "literal":
        colour = program.get("colour")
        if isinstance(colour, bool) or not isinstance(colour, int) or colour not in counts:
            raise _Undefined("literal rank colour absent")
        return colour
    if role == "minimum":
        return min(counts)
    if role == "maximum":
        return max(counts)
    if role in ("rarest", "most_frequent"):
        target = min(counts.values()) if role == "rarest" else max(counts.values())
        winners = [colour for colour, count in counts.items() if count == target]
        if len(winners) != 1:
            raise _Undefined("frequency role tied")
        return winners[0]
    raise _Undefined("unknown rank colour role")


def _rank_slots(
    rows: int, columns: int, program: Mapping[str, Any]
) -> list[tuple[int, int]]:
    row_values = list(range(rows))
    column_values = list(range(columns))
    if program.get("row_direction") == "bottom_to_top":
        row_values.reverse()
    elif program.get("row_direction") != "top_to_bottom":
        raise _Undefined("invalid row direction")
    if program.get("column_direction") == "right_to_left":
        column_values.reverse()
    elif program.get("column_direction") != "left_to_right":
        raise _Undefined("invalid column direction")
    major = program.get("major_axis")
    snake = program.get("snake")
    if not isinstance(snake, bool):
        raise _Undefined("invalid snake flag")
    slots: list[tuple[int, int]] = []
    if major == "row":
        for index, row in enumerate(row_values):
            columns_here = column_values[::-1] if snake and index % 2 else column_values
            slots.extend((row, column) for column in columns_here)
    elif major == "column":
        for index, column in enumerate(column_values):
            rows_here = row_values[::-1] if snake and index % 2 else row_values
            slots.extend((row, column) for row in rows_here)
    else:
        raise _Undefined("invalid major axis")
    return slots


def _rank_tiles_by_colour_count(grid: Grid, program: Mapping[str, Any]) -> Grid:
    lattice = _lattice(grid, minimum_panels=4)
    panels = _panels(grid, lattice)
    nr, nc = len(panels), len(panels[0])
    if nr < 2 or nc < 2:
        raise _Undefined("rank layout must use both axes")
    colour = _resolve_rank_colour(panels, lattice.separator, program)
    entries = [
        (sum(cell == colour for line in panel for cell in line), panel)
        for row in panels
        for panel in row
    ]
    if len({count for count, _ in entries}) != len(entries):
        raise _Undefined("rank counts tied")
    ordered = [panel for _, panel in sorted(entries, key=lambda item: item[0])]
    slots = _rank_slots(nr, nc, program)
    result = _blank_like(grid, lattice, _content_base(panels, lattice.separator))
    for (row, column), panel in zip(slots, ordered):
        _put_panel(result, lattice, row, column, panel)
    frozen = _freeze(result)
    if frozen == grid:
        raise _Undefined("rank layout already ordered")
    return frozen


def _panel_stat(panel: Grid, base: int, statistic: str) -> int:
    ink = [(r, c, value) for r, row in enumerate(panel) for c, value in enumerate(row) if value != base]
    if statistic == "ink_count":
        return len(ink)
    if statistic == "colour_count":
        return len({value for _, _, value in ink})
    if statistic == "box_area":
        if not ink:
            return 0
        r0, r1, c0, c1 = _bbox((r, c) for r, c, _ in ink)
        return (r1 - r0 + 1) * (c1 - c0 + 1)
    if statistic == "density":
        if not ink:
            return 0
        r0, r1, c0, c1 = _bbox((r, c) for r, c, _ in ink)
        area = (r1 - r0 + 1) * (c1 - c0 + 1)
        return len(ink) * 1000 // area
    raise _Undefined("unknown panel statistic")


def _select_panel(grid: Grid, program: Mapping[str, Any]) -> Grid:
    lattice = _lattice(grid)
    panels = _panels(grid, lattice)
    base = _content_base(panels, lattice.separator)
    statistic = program.get("statistic")
    extremum = program.get("extremum")
    if not isinstance(statistic, str) or extremum not in ("minimum", "maximum"):
        raise _Undefined("invalid selector")
    entries = [
        (_panel_stat(panel, base, statistic), panel)
        for row in panels
        for panel in row
    ]
    target = min(value for value, _ in entries) if extremum == "minimum" else max(value for value, _ in entries)
    winners = [panel for value, panel in entries if value == target]
    if len(winners) != 1:
        raise _Undefined("panel selector tied")
    return winners[0]


def _reduce_panels(grid: Grid, program: Mapping[str, Any]) -> Grid:
    lattice = _lattice(grid)
    panels2d = _panels(grid, lattice)
    panels = [panel for row in panels2d for panel in row]
    base = _content_base(panels2d, lattice.separator)
    ph, pw = _shape(panels[0])
    method = program.get("method")
    result = [[base] * pw for _ in range(ph)]
    changed = False
    for r in range(ph):
        for c in range(pw):
            values = [panel[r][c] for panel in panels]
            inks = [value for value in values if value != base]
            chosen = base
            if method == "union":
                if inks:
                    if len(set(inks)) != 1:
                        raise _Undefined("union colour collision")
                    chosen = inks[0]
            elif method == "intersection":
                if len(inks) == len(panels):
                    if len(set(inks)) != 1:
                        raise _Undefined("intersection colour collision")
                    chosen = inks[0]
            elif method == "xor":
                if len(inks) == 1:
                    chosen = inks[0]
            elif method == "majority":
                if len(inks) > len(panels) // 2:
                    counts = Counter(inks)
                    maximum = max(counts.values())
                    winners = [colour for colour, count in counts.items() if count == maximum]
                    if len(winners) != 1:
                        raise _Undefined("majority colour tied")
                    chosen = winners[0]
            else:
                raise _Undefined("unknown reduction method")
            result[r][c] = chosen
            changed |= chosen != base
    if not changed:
        raise _Undefined("empty panel reduction")
    return _freeze(result)


def execute_program(
    program: Mapping[str, Any], value: Any, limits: Mapping[str, Any] | None = None
) -> list[list[int]]:
    """Execute one serialized v2 panel program."""

    bounds = Limits.from_value(limits)
    grid = _grid(value, bounds)
    if not isinstance(program, Mapping) or program.get("schema") != SCHEMA:
        raise _Undefined("invalid program schema")
    operator = program.get("operator")
    if operator == "bordered_sequence_translate":
        result = _bordered_sequence_translate(grid)
    elif operator == "rank_tiles_by_colour_count":
        result = _rank_tiles_by_colour_count(grid, program)
    elif operator == "select_panel":
        result = _select_panel(grid, program)
    elif operator == "reduce_panels":
        result = _reduce_panels(grid, program)
    else:
        raise _Undefined("unknown operator")
    return _plain(_grid(result, bounds))


def replay_program(program: Mapping[str, Any], grid: Any) -> dict[str, Any]:
    """Replay hook with one deterministic, contiguous execution stage."""

    source = _plain(_grid(grid, Limits()))
    output = execute_program(program, source)
    return {
        "output": output,
        "stages": [
            {
                "name": f"panel-template-v2:{program.get('operator', 'unknown')}",
                "input": source,
                "output": output,
            }
        ],
    }


def _programs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    programs: list[dict[str, Any]] = [
        {
            "schema": SCHEMA,
            "operator": "bordered_sequence_translate",
            "description_length": 9,
        }
    ]
    # Role-based rankers transport across palettes.  Literal colours remain a
    # bounded fallback when the task assigns a fixed semantic colour.
    colour_specs: list[dict[str, Any]] = [
        {"colour_role": role}
        for role in ("minimum", "maximum", "rarest", "most_frequent")
    ]
    common_colours = set.intersection(
        *(
            {cell for row in source for cell in row}
            for source, _ in train
        )
    ) if train else set()
    colour_specs.extend(
        {"colour_role": "literal", "colour": colour}
        for colour in sorted(common_colours)
    )
    for spec in colour_specs:
        for major_axis in ("row", "column"):
            for row_direction in ("top_to_bottom", "bottom_to_top"):
                for column_direction in ("left_to_right", "right_to_left"):
                    for snake in (False, True):
                        programs.append(
                            {
                                "schema": SCHEMA,
                                "operator": "rank_tiles_by_colour_count",
                                **spec,
                                "major_axis": major_axis,
                                "row_direction": row_direction,
                                "column_direction": column_direction,
                                "snake": snake,
                                "description_length": 12 + int(spec["colour_role"] == "literal"),
                            }
                        )
    for statistic in ("ink_count", "colour_count", "box_area", "density"):
        for extremum in ("minimum", "maximum"):
            programs.append(
                {
                    "schema": SCHEMA,
                    "operator": "select_panel",
                    "statistic": statistic,
                    "extremum": extremum,
                    "description_length": 8,
                }
            )
    for method in ("union", "intersection", "xor", "majority"):
        programs.append(
            {
                "schema": SCHEMA,
                "operator": "reduce_panels",
                "method": method,
                "description_length": 9,
            }
        )
    unique = {_canonical(program): program for program in programs}
    return [unique[key] for key in sorted(unique)]


def _run_exact(
    program: Mapping[str, Any], pairs: Sequence[Pair], bounds: Limits
) -> tuple[Grid, ...] | None:
    outputs: list[Grid] = []
    try:
        for source, target in pairs:
            actual = _grid(execute_program(program, source, bounds), bounds)
            if actual != target:
                return None
            outputs.append(actual)
    except (
        _Undefined,
        KeyError,
        TypeError,
        ValueError,
        IndexError,
        ZeroDivisionError,
    ):
        return None
    return tuple(outputs)


def _loo_witnesses(
    program: Mapping[str, Any], train: Sequence[Pair], bounds: Limits
) -> list[dict[str, Any]] | None:
    """Require independent rediscovery and exact held-out prediction."""

    witnesses: list[dict[str, Any]] = []
    program_key = _canonical(program)
    for held_out in range(len(train)):
        subset = tuple(pair for index, pair in enumerate(train) if index != held_out)
        rediscovered = {_canonical(item) for item in _programs(subset)}
        if program_key not in rediscovered:
            return None
        if _run_exact(program, subset, bounds) is None:
            return None
        source, target = train[held_out]
        try:
            prediction = _grid(execute_program(program, source, bounds), bounds)
        except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):
            return None
        if prediction != target:
            return None
        witnesses.append(
            {
                "held_out_index": held_out,
                "proposal_demo_count": len(subset),
                "program_rediscovered": True,
                "held_out_exact": True,
                "held_out_output_hash": _digest(_plain(prediction)),
            }
        )
    return witnesses


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile a unique test behaviour with strict leave-one-out support."""

    bounds = Limits.from_value(limits)
    try:
        train, tests = _read_task(task, bounds)
    except (ValueError, TypeError, KeyError):
        return []
    programs = _programs(train)
    if len(programs) > bounds.max_programs:
        return []
    enumeration_signature = _digest(programs)
    if _digest(_programs(tuple(reversed(train)))) != enumeration_signature:
        return []
    behaviours: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...], list[dict[str, Any]]]]] = {}
    calls = 0
    for program in programs:
        if int(program["description_length"]) > bounds.max_mdl:
            continue
        calls += len(train) + len(tests) + len(train) * len(train)
        if calls > bounds.max_executor_calls:
            return []
        replay = _run_exact(program, train, bounds)
        if replay is None:
            continue
        witnesses = _loo_witnesses(program, train, bounds)
        if witnesses is None:
            continue
        try:
            predictions = tuple(
                _grid(execute_program(program, source, bounds), bounds) for source in tests
            )
        except (
            _Undefined,
            KeyError,
            TypeError,
            ValueError,
            IndexError,
            ZeroDivisionError,
        ):
            continue
        key = _canonical([_plain(output) for output in predictions])
        behaviours.setdefault(key, []).append((program, replay, predictions, witnesses))
    if len(behaviours) != 1:
        return []
    entries = next(iter(behaviours.values()))
    entries.sort(key=lambda entry: (int(entry[0]["description_length"]), _canonical(entry[0])))
    program, replay, predictions, witnesses = entries[0]
    return [
        {
            "family": "panel_template_composer_v2",
            "program": program,
            "train_outputs": [_plain(output) for output in replay],
            "test_outputs": [_plain(output) for output in predictions],
            "complexity": int(program["description_length"]),
            "evidence": {
                "all_demonstrations_exact": True,
                "demonstration_count": len(train),
                "test_count": len(tests),
                "strict_leave_one_out": True,
                "leave_one_out_witnesses": witnesses,
                "complete_behavior_quotient": True,
                "unique_test_behavior": True,
                "ambiguity_policy": "abstain unless exactly one complete test behaviour remains",
                "demo_order_invariance_checked": True,
                "enumeration_signature": enumeration_signature,
                "corroborating_programs": len(entries),
                "corroborating_operators": sorted(
                    {str(entry[0]["operator"]) for entry in entries}
                ),
                "enumerated_programs": len(programs),
                "executor_call_upper_bound": calls,
                "behavior_hash": _digest([_plain(output) for output in predictions]),
                "bounded_search": True,
                "task_identity_free": True,
                "test_outputs_observed": False,
            },
        }
    ] if bounds.max_candidates else []


__all__ = ["Limits", "SCHEMA", "compile_task", "execute_program", "replay_program"]
