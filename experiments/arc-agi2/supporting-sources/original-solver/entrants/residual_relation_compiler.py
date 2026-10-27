"""Retrospective relational residual schemas for PR-LASM Block 15.

The operators here were designed after inspecting scored public-training
residuals.  This is therefore score-seeded development, not hidden-test or
transfer evidence.  Runtime compilation remains task-local: it receives one
challenge, ignores any attached test outputs, learns only from demonstrations,
requires exact replay and leave-one-demonstration-out re-induction, and has no
task-identity, corpus, score, or solution-store interface.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import json
from typing import Any, Iterable


AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.residual_relation.program.v1"
DEVELOPMENT_REGIME = "retrospective_score_seeded_public_training"

Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
Pair = tuple[Grid, Grid]


class Undefined(ValueError):
    """A finite structural contract is absent or ambiguous."""


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
        if (
            not isinstance(raw_row, Sequence)
            or isinstance(raw_row, (str, bytes))
            or not raw_row
        ):
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for raw_cell in raw_row:
            if (
                isinstance(raw_cell, bool)
                or not isinstance(raw_cell, int)
                or not 0 <= raw_cell <= 9
            ):
                raise Undefined("ARC colors must be integers in [0, 9]")
            row.append(int(raw_cell))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise Undefined("grid is ragged")
        rows.append(tuple(row))
    if len(rows) * int(width or 0) > 900:
        raise Undefined("grid exceeds the finite cell bound")
    return tuple(rows)


def _plain(value: Grid) -> list[list[int]]:
    return [list(row) for row in value]


def _shape(value: Grid) -> tuple[int, int]:
    return len(value), len(value[0])


def _sanitize(task: Any) -> tuple[tuple[Pair, ...], tuple[Grid, ...]]:
    if not isinstance(task, Mapping):
        raise Undefined("task must be a mapping")
    raw_train, raw_test = task.get("train"), task.get("test")
    if (
        not isinstance(raw_train, Sequence)
        or isinstance(raw_train, (str, bytes))
        or not 2 <= len(raw_train) <= 16
        or not isinstance(raw_test, Sequence)
        or isinstance(raw_test, (str, bytes))
        or not 1 <= len(raw_test) <= 4
    ):
        raise Undefined("bounded train and test splits are required")
    train: list[Pair] = []
    for record in raw_train:
        if not isinstance(record, Mapping):
            raise Undefined("invalid demonstration record")
        train.append((_grid(record.get("input")), _grid(record.get("output"))))
    tests: list[Grid] = []
    for record in raw_test:
        if not isinstance(record, Mapping):
            raise Undefined("invalid test record")
        # Held-out labels are deliberately ignored even when injected.
        tests.append(_grid(record.get("input")))
    return tuple(train), tuple(tests)


def _strict_mode(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    peak = max(counts.values())
    winners = [color for color, count in counts.items() if count == peak]
    if len(winners) != 1:
        raise Undefined("modal background is tied")
    return winners[0]


def _components(value: Grid, background: int, *, monochrome: bool) -> tuple[tuple[Cell, ...], ...]:
    height, width = _shape(value)
    seen: set[Cell] = set()
    result: list[tuple[Cell, ...]] = []
    for row in range(height):
        for column in range(width):
            if value[row][column] == background or (row, column) in seen:
                continue
            seed_color = value[row][column]
            queue = [(row, column)]
            seen.add((row, column))
            component: list[Cell] = []
            while queue:
                current = queue.pop()
                component.append(current)
                for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    neighbor = (current[0] + delta_row, current[1] + delta_column)
                    if not (0 <= neighbor[0] < height and 0 <= neighbor[1] < width):
                        continue
                    if neighbor in seen or value[neighbor[0]][neighbor[1]] == background:
                        continue
                    if monochrome and value[neighbor[0]][neighbor[1]] != seed_color:
                        continue
                    seen.add(neighbor)
                    queue.append(neighbor)
            result.append(tuple(sorted(component)))
    return tuple(result)


def _execute_occluded_supports(value: Grid) -> Grid:
    """Restore rectangles and 45-degree lines overwritten only by other objects."""

    background = _strict_mode(value)
    height, width = _shape(value)
    writes: dict[Cell, int] = {}
    colors = sorted({cell for row in value for cell in row} - {background})
    for color in colors:
        cells = [(row, column) for row in range(height) for column in range(width) if value[row][column] == color]
        if len(cells) < 3:
            continue
        row_min = min(row for row, _ in cells)
        row_max = max(row for row, _ in cells)
        column_min = min(column for _, column in cells)
        column_max = max(column for _, column in cells)
        box = [
            (row, column)
            for row in range(row_min, row_max + 1)
            for column in range(column_min, column_max + 1)
        ]
        if len(box) > len(cells) and all(value[row][column] != background for row, column in box):
            for cell in box:
                if value[cell[0]][cell[1]] == color:
                    continue
                if cell in writes and writes[cell] != color:
                    raise Undefined("overlapping occluded supports disagree")
                writes[cell] = color
        for anti_diagonal in (False, True):
            invariants = {
                row + column if anti_diagonal else row - column
                for row, column in cells
            }
            if len(invariants) != 1:
                continue
            invariant = next(iter(invariants))
            path = [
                (
                    row,
                    invariant - row if anti_diagonal else row - invariant,
                )
                for row in range(row_min, row_max + 1)
            ]
            if (
                len(path) <= len(cells)
                or not all(0 <= column < width and value[row][column] != background for row, column in path)
            ):
                continue
            for cell in path:
                if value[cell[0]][cell[1]] == color:
                    continue
                if cell in writes and writes[cell] != color:
                    raise Undefined("overlapping occluded supports disagree")
                writes[cell] = color
    if not writes:
        raise Undefined("no occluded support is present")
    output = [list(row) for row in value]
    for (row, column), color in sorted(writes.items()):
        output[row][column] = color
    return tuple(tuple(row) for row in output)


def _enclosed_area(value: Grid, cells: frozenset[Cell]) -> int:
    row_min = min(row for row, _ in cells)
    row_max = max(row for row, _ in cells)
    column_min = min(column for _, column in cells)
    column_max = max(column for _, column in cells)
    complement = {
        (row, column)
        for row in range(row_min, row_max + 1)
        for column in range(column_min, column_max + 1)
        if (row, column) not in cells
    }
    exterior = {
        cell
        for cell in complement
        if cell[0] in {row_min, row_max} or cell[1] in {column_min, column_max}
    }
    queue = list(exterior)
    for current in queue:
        for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (current[0] + delta_row, current[1] + delta_column)
            if neighbor in complement and neighbor not in exterior:
                exterior.add(neighbor)
                queue.append(neighbor)
    return len(complement - exterior)


def _execute_void_histogram(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    output_height = int(program["output_height"])
    output_width = int(program["output_width"])
    objects = list(_components(value, background, monochrome=True))
    if len(objects) != 2 or output_height < 1 or output_width < 1:
        raise Undefined("two monochrome pierced objects are required")
    objects.sort(key=lambda component: min(column for _, column in component))
    if max(column for _, column in objects[0]) >= min(column for _, column in objects[1]):
        raise Undefined("object ordering is not separated")
    output = [[background] * output_width for _ in range(output_height)]
    output_row = 0
    for component in objects:
        colors = {value[row][column] for row, column in component}
        if len(colors) != 1:
            raise Undefined("object is not monochrome")
        color = next(iter(colors))
        area = _enclosed_area(value, frozenset(component))
        if area < 1:
            raise Undefined("object has no enclosed void")
        for index in range(area):
            row = output_row + index // output_width
            if row >= output_height:
                raise Undefined("histogram exceeds the learned canvas")
            output[row][index % output_width] = color
        output_row += (area + output_width - 1) // output_width
    if output_row > output_height:
        raise Undefined("histogram exceeds the learned canvas")
    return tuple(tuple(row) for row in output)


def _learn_void_histogram(train: Sequence[Pair]) -> dict[str, Any] | None:
    output_shapes = {_shape(target) for _, target in train}
    if len(output_shapes) != 1:
        return None
    output_height, output_width = next(iter(output_shapes))
    common_colors = set(range(10))
    for source, _ in train:
        common_colors &= {cell for row in source for cell in row}
    programs: list[dict[str, Any]] = []
    for background in sorted(common_colors):
        program = {
            "schema": SCHEMA,
            "operator": "void_histogram",
            "background": background,
            "output_height": output_height,
            "output_width": output_width,
            "description_length": 19,
        }
        try:
            if all(_execute_void_histogram(source, program) == target for source, target in train):
                programs.append(program)
        except Undefined:
            continue
    return programs[0] if len(programs) == 1 else None


def _execute_safe_route(value: Grid, program: Mapping[str, Any]) -> Grid:
    source_color = int(program["source_color"])
    route_color = int(program["route_color"])
    height, width = _shape(value)
    nodes = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] in {source_color, route_color}
    }
    endpoints = sorted(cell for cell in nodes if value[cell[0]][cell[1]] == route_color)
    if len(endpoints) != 2 or len(nodes) > 64:
        raise Undefined("route requires exactly two bounded endpoint markers")
    remaining = Counter(
        value[row][column]
        for row in range(height)
        for column in range(width)
        if value[row][column] not in {source_color, route_color}
    )
    if not remaining:
        raise Undefined("route has no background")
    peak = max(remaining.values())
    backgrounds = [color for color, count in remaining.items() if count == peak]
    if len(backgrounds) != 1:
        raise Undefined("route background is tied")
    background = backgrounds[0]
    blockers = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] not in {source_color, route_color, background}
    }
    if not blockers:
        raise Undefined("a blocker witness is required")
    paths: set[frozenset[Cell]] = set()
    calls = 0

    def visit(current: Cell, seen: tuple[Cell, ...]) -> None:
        nonlocal calls
        calls += 1
        if calls > 200_000:
            raise Undefined("route enumeration limit exceeded")
        if current == endpoints[1]:
            paths.add(frozenset(seen))
            return
        for delta_row, delta_column in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (current[0] + delta_row, current[1] + delta_column)
            if neighbor in nodes and neighbor not in seen:
                visit(neighbor, seen + (neighbor,))

    visit(endpoints[0], (endpoints[0],))
    safe = [
        path
        for path in paths
        if not any(
            abs(row - blocker_row) + abs(column - blocker_column) == 1
            for row, column in path
            for blocker_row, blocker_column in blockers
        )
    ]
    if not safe:
        raise Undefined("no blocker-avoiding route exists")

    def border_cost(path: frozenset[Cell]) -> int:
        return sum(
            min(row, height - 1 - row, column, width - 1 - column)
            for row, column in path
        )

    optimum = min(border_cost(path) for path in safe)
    winners = [path for path in safe if border_cost(path) == optimum]
    if len(winners) != 1:
        raise Undefined("outermost safe route is ambiguous")
    output = [list(row) for row in value]
    for row, column in winners[0]:
        output[row][column] = route_color
    return tuple(tuple(row) for row in output)


def _learn_safe_route(train: Sequence[Pair]) -> dict[str, Any] | None:
    transition: tuple[int, int] | None = None
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        changes = {
            (before, after)
            for source_row, target_row in zip(source, target)
            for before, after in zip(source_row, target_row)
            if before != after
        }
        if len(changes) != 1:
            return None
        current = next(iter(changes))
        if transition is None:
            transition = current
        elif transition != current:
            return None
    if transition is None:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "safe_route",
        "source_color": transition[0],
        "route_color": transition[1],
        "description_length": 23,
    }
    try:
        return program if all(_execute_safe_route(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute_corner_stencils(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _strict_mode(value)
    height, width = _shape(value)
    seeds = [
        (row, column, value[row][column])
        for row in range(height)
        for column in range(width)
        if value[row][column] != background
    ]
    if not seeds:
        raise Undefined("no corner seeds")
    output = [list(row) for row in value]
    for row, column, color in seeds:
        if row not in {0, height - 1} or column not in {0, width - 1}:
            raise Undefined("every signal must be a corner singleton")
        output[row][column] = background
        side = "top" if row == 0 else "bottom"
        raw_stencil = program.get(f"{side}_stencil")
        if not isinstance(raw_stencil, Sequence):
            raise Undefined("corner stencil is missing")
        for raw_offset in raw_stencil:
            if not isinstance(raw_offset, Sequence) or len(raw_offset) != 2:
                raise Undefined("corner offset is invalid")
            delta_row, delta_column = int(raw_offset[0]), int(raw_offset[1])
            target_row = delta_row if row == 0 else height - 1 - delta_row
            target_column = delta_column if column == 0 else width - 1 - delta_column
            if (
                not 0 <= target_row < height
                or not 0 <= target_column < width
                or value[target_row][target_column] != background
            ):
                raise Undefined("corner stencil collides or exits the grid")
            output[target_row][target_column] = color
    return tuple(tuple(row) for row in output)


def _learn_corner_stencils(train: Sequence[Pair]) -> dict[str, Any] | None:
    examples: dict[str, list[tuple[Cell, ...]]] = {"top": [], "bottom": []}
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        try:
            background = _strict_mode(source)
        except Undefined:
            return None
        height, width = _shape(source)
        seeds = [
            (row, column, source[row][column])
            for row in range(height)
            for column in range(width)
            if source[row][column] != background
        ]
        if len(seeds) != 1:
            return None
        row, column, color = seeds[0]
        if row not in {0, height - 1} or column not in {0, width - 1}:
            return None
        if target[row][column] != background or any(cell not in {background, color} for target_row in target for cell in target_row):
            return None
        offsets: list[Cell] = []
        for target_row in range(height):
            for target_column in range(width):
                if target[target_row][target_column] != color:
                    continue
                delta_row = target_row if row == 0 else height - 1 - target_row
                delta_column = target_column if column == 0 else width - 1 - target_column
                offsets.append((delta_row, delta_column))
        if not offsets:
            return None
        examples["top" if row == 0 else "bottom"].append(tuple(sorted(offsets)))
    if not examples["top"] or not examples["bottom"]:
        return None
    if len(set(examples["top"])) != 1 or len(set(examples["bottom"])) != 1:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "corner_stencils",
        "top_stencil": [list(cell) for cell in examples["top"][0]],
        "bottom_stencil": [list(cell) for cell in examples["bottom"][0]],
        "description_length": 17 + len(examples["top"][0]) + len(examples["bottom"][0]),
    }
    try:
        return program if all(_execute_corner_stencils(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute_pair_compaction(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    pairs = {tuple(sorted((int(pair[0]), int(pair[1])))) for pair in program["pairs"]}
    output: list[tuple[int, ...]] = []
    changes = 0
    for row in value:
        occupied = [column for column, color in enumerate(row) if color != background]
        rendered = list(row)
        if (
            len(occupied) == 2
            and tuple(sorted((row[occupied[0]], row[occupied[1]]))) in pairs
            and occupied[1] > occupied[0] + 1
        ):
            left, right = occupied
            rendered[left] = background
            rendered[right] = background
            rendered[left] = row[left]
            rendered[left + 1] = row[right]
            changes += 1
        output.append(tuple(rendered))
    if not changes:
        raise Undefined("no learned pair requires compaction")
    return tuple(output)


def _learn_pair_compaction(train: Sequence[Pair]) -> dict[str, Any] | None:
    background: int | None = None
    pairs: set[tuple[int, int]] = set()
    changed_rows = 0
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        try:
            current_background = _strict_mode(source)
        except Undefined:
            return None
        if background is None:
            background = current_background
        elif background != current_background:
            return None
        for source_row, target_row in zip(source, target):
            if source_row == target_row:
                continue
            occupied = [column for column, color in enumerate(source_row) if color != background]
            if len(occupied) != 2:
                return None
            left, right = occupied
            expected = list(source_row)
            expected[left] = background
            expected[right] = background
            expected[left] = source_row[left]
            expected[left + 1] = source_row[right]
            if tuple(expected) != target_row:
                return None
            pairs.add(tuple(sorted((source_row[left], source_row[right]))))
            changed_rows += 1
    if background is None or len(pairs) < 2 or changed_rows < 2:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "pair_compaction",
        "background": background,
        "pairs": [list(pair) for pair in sorted(pairs)],
        "description_length": 16 + len(pairs),
    }
    try:
        return program if all(_execute_pair_compaction(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute_diversity_bars(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = _strict_mode(value)
    fill_color = int(program["fill_color"])
    objects = _components(value, background, monochrome=False)
    if not objects:
        raise Undefined("no code blocks")
    output = [list(row) for row in value]
    height, _ = _shape(value)
    for component in objects:
        rows = [row for row, _ in component]
        columns = [column for _, column in component]
        row_min, row_max = min(rows), max(rows)
        column_min, column_max = min(columns), max(columns)
        if row_max - row_min != 1 or column_max - column_min != 1 or len(component) != 4:
            raise Undefined("every code block must be a filled two-by-two square")
        diversity = len({value[row][column] for row, column in component})
        if row_max + diversity >= height:
            raise Undefined("diversity bar exits the grid")
        for row in range(row_max + 1, row_max + diversity + 1):
            for column in range(column_min, column_max + 1):
                if value[row][column] != background:
                    raise Undefined("diversity bar collides")
                output[row][column] = fill_color
    return tuple(tuple(row) for row in output)


def _learn_diversity_bars(train: Sequence[Pair]) -> dict[str, Any] | None:
    fill_colors: set[int] = set()
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        source_colors = {cell for row in source for cell in row}
        fill_colors |= {
            after
            for source_row, target_row in zip(source, target)
            for before, after in zip(source_row, target_row)
            if before != after and after not in source_colors
        }
    if len(fill_colors) != 1:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "diversity_bars",
        "fill_color": next(iter(fill_colors)),
        "description_length": 18,
    }
    try:
        return program if all(_execute_diversity_bars(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute(program: Mapping[str, Any], value: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    operator = program.get("operator")
    if operator == "occluded_supports":
        return _execute_occluded_supports(value)
    if operator == "void_histogram":
        return _execute_void_histogram(value, program)
    if operator == "safe_route":
        return _execute_safe_route(value, program)
    if operator == "corner_stencils":
        return _execute_corner_stencils(value, program)
    if operator == "pair_compaction":
        return _execute_pair_compaction(value, program)
    if operator == "diversity_bars":
        return _execute_diversity_bars(value, program)
    raise Undefined("unknown residual relation operator")


def _programs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    programs: list[dict[str, Any]] = [
        {
            "schema": SCHEMA,
            "operator": "occluded_supports",
            "description_length": 14,
        }
    ]
    for learner in (
        _learn_void_histogram,
        _learn_safe_route,
        _learn_corner_stencils,
        _learn_pair_compaction,
        _learn_diversity_bars,
    ):
        program = learner(train)
        if program is not None:
            programs.append(program)
    return programs


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized, task-local program."""

    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    source = _grid(value)
    lifted = {
        "kind": "residual_relation_scene",
        "shape": list(_shape(source)),
        "operator": program.get("operator"),
    }
    output = _execute(program, source)
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-relational-scene", "input": _plain(source), "output": lifted},
            {"name": "execute-relational-schema", "input": lifted, "output": _plain(output)},
        ],
    }


def compile_task(task: Any, limits: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compile one unique exact-replay behavior or abstain."""

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
    exact: list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]] = []
    programs = _programs(train)
    for program in programs:
        try:
            train_outputs = tuple(_execute(program, source) for source, _ in train)
            if train_outputs != tuple(target for _, target in train):
                continue
            test_outputs = tuple(_execute(program, source) for source in tests)
        except (Undefined, TypeError, ValueError, KeyError, IndexError, RecursionError):
            continue
        exact.append((program, train_outputs, test_outputs))
    if not exact:
        return []
    behaviors: dict[str, list[tuple[dict[str, Any], tuple[Grid, ...], tuple[Grid, ...]]]] = {}
    for record in exact:
        behavior_hash = _digest([_plain(grid) for grid in record[2]])
        behaviors.setdefault(behavior_hash, []).append(record)
    if len(behaviors) != 1:
        return []
    behavior_hash, equivalent = next(iter(sorted(behaviors.items())))
    equivalent.sort(key=lambda record: (int(record[0]["description_length"]), _canonical(record[0])))
    program, train_outputs, test_outputs = equivalent[0]
    operator = program["operator"]
    reinductions: list[dict[str, Any]] = []
    for held_index, (held_source, held_target) in enumerate(train):
        reduced = train[:held_index] + train[held_index + 1 :]
        witnesses: list[dict[str, Any]] = []
        for witness in _programs(reduced):
            if witness.get("operator") != operator:
                continue
            try:
                if any(_execute(witness, source) != target for source, target in reduced):
                    continue
                if _execute(witness, held_source) != held_target:
                    continue
                if tuple(_execute(witness, source) for source in tests) != test_outputs:
                    continue
            except (Undefined, TypeError, ValueError, KeyError, IndexError, RecursionError):
                continue
            witnesses.append(witness)
        if not witnesses:
            return []
        reinductions.append(
            {
                "held_out_index": held_index,
                "exact": True,
                "witness_count": len(witnesses),
                "held_output_hash": _digest(_plain(held_target)),
            }
        )
    candidate = {
        "family": "residual_relation_compiler",
        "program": json.loads(_canonical(program)),
        "train_outputs": [_plain(grid) for grid in train_outputs],
        "test_outputs": [_plain(grid) for grid in test_outputs],
        "complexity": int(program["description_length"]),
        "evidence": {
            "development_boundary": DEVELOPMENT_REGIME,
            "development_solution_store_observed": True,
            "solution_store_observed_at_runtime": False,
            "task_identity_observed": False,
            "test_labels_observed_at_runtime": False,
            "all_demonstrations_exact": True,
            "leave_one_out_reinduction": reinductions,
            "programs_enumerated": len(programs),
            "exact_programs": len(exact),
            "full_test_behavior_classes": 1,
            "full_test_behavior_hash": behavior_hash,
            "bounded_search": True,
        },
    }
    candidate["evidence"]["candidate_semantic_hash"] = _digest(candidate)
    return [candidate][:cap]


__all__ = ["AUTHOR", "SCHEMA", "compile_task", "execute_program", "replay_program"]
