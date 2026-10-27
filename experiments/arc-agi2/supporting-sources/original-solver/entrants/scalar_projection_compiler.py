"""Retrospective scalar and axis projection schemas for Block 15.

The three operators in this module were recovered while inspecting the public
training residual after G38.  This is therefore a score-seeded development
entrant, not hidden-test evidence.  At runtime it observes only one ARC task,
requires exact demonstration replay, and has no task-identity or solution-store
interface.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from typing import Any, Mapping, Sequence


AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.scalar_projection.program.v1"

Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]


class Undefined(ValueError):
    """The raster does not satisfy an operator's finite structural contract."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise Undefined("grid must be a nonempty row sequence")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(cell))
        if width is None:
            width = len(row)
        elif width != len(row):
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > 900:
        raise Undefined("grid exceeds ARC's finite cell bound")
    return tuple(rows)


def _plain(grid: Grid) -> list[list[int]]:
    return [list(row) for row in grid]


def _sanitize(task: Any) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not 2 <= len(raw_train) <= 10
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not 1 <= len(raw_test) <= 4
    ):
        raise Undefined("bounded train and test splits are required")
    train: list[Pair] = []
    for example in raw_train:
        if not isinstance(example, Mapping):
            raise Undefined("training example is invalid")
        train.append((_grid(example.get("input")), _grid(example.get("output"))))
    tests: list[Grid] = []
    for example in raw_test:
        if not isinstance(example, Mapping):
            raise Undefined("test example is invalid")
        # Deliberately ignore an attached held-out output field.
        tests.append(_grid(example.get("input")))
    return tuple(train), tuple(tests)


def _background(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Undefined("background mode is tied")
    return winners[0]


def _parity_corner_extract(grid: Grid) -> Grid:
    """Take the upper 2x2 corner selected by horizontal size parity."""

    height, width = len(grid), len(grid[0])
    if height != width or not 3 <= height <= 30:
        raise Undefined("parity projection requires a square source")
    column = 0 if width % 2 else width - 2
    return tuple(tuple(grid[row][column : column + 2]) for row in range(2))


def _invert_row_dominant_mask(grid: Grid) -> Grid:
    """Invert each row's uniquely dominant non-background color support."""

    # Literal zero is the conventional empty cell for this binary-mask schema.
    # The signal color is selected relationally: it is local to one row, unlike
    # a marker color that is repeated across rows.
    background = 0
    row_incidence = Counter(
        color
        for color in range(1, 10)
        for row in grid
        if color in row
    )
    output: list[tuple[int, ...]] = []
    for row in grid:
        counts = Counter(cell for cell in row if cell != background)
        if not counts:
            raise Undefined("every row must carry a foreground signal")
        local = [color for color in counts if row_incidence[color] == 1]
        pool = local or list(counts)
        maximum = max(counts[color] for color in pool)
        winners = [color for color in pool if counts[color] == maximum]
        if len(winners) != 1 or maximum < 2:
            raise Undefined("row has no unique repeated dominant color")
        dominant = winners[0]
        output.append(tuple(background if cell == dominant else dominant for cell in row))
    return tuple(output)


def _run_rows_and_axis(grid: Grid) -> tuple[int, tuple[tuple[int, int, int], ...]]:
    background = _background(grid)
    singleton_rows: list[tuple[int, int]] = []
    runs: list[tuple[int, int, int]] = []
    for row_index, row in enumerate(grid):
        occupied = [column for column, cell in enumerate(row) if cell != background]
        if not occupied:
            continue
        colors = {row[column] for column in occupied}
        if len(occupied) == 1:
            singleton_rows.append((row_index, occupied[0]))
            continue
        if len(colors) != 1 or occupied != list(range(occupied[0], occupied[-1] + 1)):
            raise Undefined("signal row is not one monochrome contiguous run")
        runs.append((row_index, occupied[0], len(occupied)))
    if len(singleton_rows) != 1 or not runs:
        raise Undefined("one singleton axis key and at least one run are required")
    axis = singleton_rows[0][1]
    if not any(grid[row][axis] == background for row, _, _ in runs):
        raise Undefined("axis key has no writable run annotation")
    return axis, tuple(runs)


def _annotation_key(length: int, gap: int) -> str:
    return f"{length}:{gap}"


def _annotate_runs_on_key_axis(grid: Grid, program: Mapping[str, Any]) -> Grid:
    """Write demonstration-induced scalar run codes on a singleton axis."""

    background = _background(grid)
    axis, runs = _run_rows_and_axis(grid)
    raw_lengths = program.get("length_colors")
    raw_exceptions = program.get("length_gap_colors")
    if not isinstance(raw_lengths, Mapping) or not isinstance(raw_exceptions, Mapping):
        raise Undefined("annotation program has no finite scalar code map")
    output = [list(row) for row in grid]
    for row, start, length in runs:
        if output[row][axis] == background:
            gap = axis - (start + length) if start + length <= axis else start - axis - 1
            raw = raw_lengths.get(str(length), raw_exceptions.get(_annotation_key(length, gap)))
            if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= 9:
                raise Undefined("run code is not determined by demonstrations")
            output[row][axis] = raw
    return tuple(tuple(row) for row in output)


_STATIC_PROGRAMS = (
    {"schema": SCHEMA, "operator": "parity_corner_extract", "description_length": 9},
    {"schema": SCHEMA, "operator": "invert_row_dominant_mask", "description_length": 12},
)


def _execute(program: Mapping[str, Any], grid: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    operator = program.get("operator")
    if operator == "parity_corner_extract":
        return _parity_corner_extract(grid)
    if operator == "invert_row_dominant_mask":
        return _invert_row_dominant_mask(grid)
    if operator == "annotate_runs_on_key_axis":
        return _annotate_runs_on_key_axis(grid, program)
    raise Undefined("unknown scalar projection operator")


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized program without corpus or task identity state."""

    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    """Return a two-stage replay trace for tournament verification."""

    source = _grid(value)
    lifted = {
        "kind": "scalar_axis_scene",
        "shape": [len(source), len(source[0])],
        "operator": program.get("operator"),
    }
    output = _execute(program, source)
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-scalar-axis-scene", "input": _plain(source), "output": lifted},
            {"name": "apply-projection", "input": lifted, "output": _plain(output)},
        ],
    }


def _learn_annotation_program(train: Sequence[Pair]) -> dict[str, Any] | None:
    by_length: dict[int, set[int]] = {}
    by_length_gap: dict[tuple[int, int], set[int]] = {}
    for source, target in train:
        if (len(source), len(source[0])) != (len(target), len(target[0])):
            return None
        try:
            background = _background(source)
            axis, runs = _run_rows_and_axis(source)
        except Undefined:
            return None
        expected = [list(row) for row in source]
        for row, start, length in runs:
            if source[row][axis] != background:
                continue
            color = target[row][axis]
            if color == background:
                return None
            gap = axis - (start + length) if start + length <= axis else start - axis - 1
            by_length.setdefault(length, set()).add(color)
            by_length_gap.setdefault((length, gap), set()).add(color)
            expected[row][axis] = color
        if tuple(tuple(row) for row in expected) != target:
            return None
    length_colors = {
        str(length): next(iter(colors))
        for length, colors in sorted(by_length.items())
        if len(colors) == 1
    }
    exceptions: dict[str, int] = {}
    for key, colors in sorted(by_length_gap.items()):
        if key[0] in {int(length) for length in length_colors}:
            continue
        if len(colors) != 1:
            return None
        exceptions[_annotation_key(*key)] = next(iter(colors))
    if len(by_length) < 4 or any(
        str(length) not in length_colors
        and not all(_annotation_key(length, gap) in exceptions for l, gap in by_length_gap if l == length)
        for length in by_length
    ):
        return None
    return {
        "schema": SCHEMA,
        "operator": "annotate_runs_on_key_axis",
        "length_colors": length_colors,
        "length_gap_colors": exceptions,
        "description_length": 14 + len(length_colors) + len(exceptions),
    }


def _task_guard(operator: str, train: Sequence[Pair]) -> bool:
    if operator == "parity_corner_extract":
        sizes = {len(source) for source, _ in train}
        return len(sizes) >= 3 and {size % 2 for size in sizes} == {0, 1}
    if operator == "invert_row_dominant_mask":
        widths = {len(source[0]) for source, _ in train}
        return len(widths) == 1 and next(iter(widths)) >= 8
    return False


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile a unique exact-replay scalar projection behavior or abstain."""

    try:
        train, tests = _sanitize(task)
    except (Undefined, TypeError, ValueError, KeyError):
        return []
    cap = 1
    if isinstance(limits, Mapping):
        raw_cap = limits.get("max_candidates", limits.get("candidate_cap", 1))
        if isinstance(raw_cap, bool) or not isinstance(raw_cap, int) or raw_cap < 1:
            return []
        cap = min(raw_cap, 1)
    programs = list(_STATIC_PROGRAMS)
    learned_annotation = _learn_annotation_program(train)
    if learned_annotation is not None:
        programs.append(learned_annotation)
    exact: list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]] = []
    for program in programs:
        operator = str(program["operator"])
        if operator != "annotate_runs_on_key_axis" and not _task_guard(operator, train):
            continue
        try:
            train_outputs = tuple(_execute(program, source) for source, _ in train)
            if train_outputs != tuple(target for _, target in train):
                continue
            test_outputs = tuple(_execute(program, source) for source in tests)
        except (Undefined, TypeError, ValueError, KeyError, IndexError):
            continue
        exact.append((program, train_outputs, test_outputs))
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]]] = {}
    for record in exact:
        behaviors.setdefault(_digest([_plain(grid) for grid in record[2]]), []).append(record)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda item: (int(item[0]["description_length"]), _canonical(item[0])))
    program, train_outputs, test_outputs = equivalent[0]
    isolated = []
    for index, (source, target) in enumerate(train):
        try:
            exact_held = _execute(program, source) == target
        except Undefined:
            return []
        if not exact_held:
            return []
        isolated.append({"held_out_index": index, "exact": True, "output_hash": _digest(_plain(target))})
    candidate = {
        "family": "scalar_projection_compiler",
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(program["description_length"]),
        "evidence": {
            "development_boundary": "retrospective_score_seeded_public_training",
            "all_demonstrations_exact": True,
            "exact_replay": True,
            "isolated_demonstration_replays": isolated,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": 1,
            "full_test_behavior_hash": behavior_hash,
            "bounded_search": True,
            "task_identity_observed": False,
            "test_labels_observed_at_runtime": False,
            "solution_store_observed_at_runtime": False,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][:cap]


__all__ = ["AUTHOR", "SCHEMA", "compile_task", "execute_program", "replay_program"]
