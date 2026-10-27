"""Retrospective selector, glyph, and layout schemas for PR-LASM Block 15.

These operators were developed after inspecting scored ARC public-training
residuals.  The development regime is therefore score-seeded and is not
evidence about hidden-test transfer.  At runtime the compiler receives only
one sanitized challenge, learns all roles from its demonstrations, ignores
any attached test labels, and has no task-identity, corpus, or solution-store
interface.

Author: Komorebi P.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import json
from typing import Any


AUTHOR = "Komorebi P."
SCHEMA = "komorebi.pr_lasm.block15.selector_glyph.program.v1"
DEVELOPMENT_REGIME = "retrospective_score_seeded_public_training"

Grid = tuple[tuple[int, ...], ...]
Pair = tuple[Grid, Grid]
Cell = tuple[int, int]


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
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes)) or not raw_row:
            raise Undefined("grid row is invalid")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, int) or not 0 <= raw_cell <= 9:
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
        # Deliberately ignore an injected held-out output.
        tests.append(_grid(record.get("input")))
    return tuple(train), tuple(tests)


def _strict_mode(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    peak = max(counts.values())
    winners = [color for color, count in counts.items() if count == peak]
    if len(winners) != 1:
        raise Undefined("modal background is tied")
    return winners[0]


def _eight_components(value: Grid, color: int) -> tuple[tuple[Cell, ...], ...]:
    height, width = _shape(value)
    remaining = {
        (row, column)
        for row in range(height)
        for column in range(width)
        if value[row][column] == color
    }
    result: list[tuple[Cell, ...]] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue = [seed]
        component: list[Cell] = []
        while queue:
            row, column = queue.pop()
            component.append((row, column))
            for delta_row in (-1, 0, 1):
                for delta_column in (-1, 0, 1):
                    if delta_row == delta_column == 0:
                        continue
                    neighbor = (row + delta_row, column + delta_column)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        queue.append(neighbor)
        result.append(tuple(sorted(component)))
    return tuple(result)


def _execute_component_histogram(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    width = int(program["width"])
    column_by_color = {int(color): int(column) for color, column in program["column_by_color"]}
    if _strict_mode(value) != background or width < 2 or len(column_by_color) < 4:
        raise Undefined("histogram canvas roles are absent")
    colors = sorted({cell for row in value for cell in row} - {background})
    if not colors or any(color not in column_by_color for color in colors):
        raise Undefined("an unseen histogram category is present")
    counts = {color: len(_eight_components(value, color)) for color in colors}
    if any(count < 1 for count in counts.values()):
        raise Undefined("empty histogram category")
    height = max(counts.values())
    if height > 30:
        raise Undefined("histogram exceeds the ARC bound")
    output = [[background] * width for _ in range(height)]
    for color, count in sorted(counts.items()):
        column = column_by_color[color]
        if not 0 <= column < width:
            raise Undefined("histogram column is out of range")
        for row in range(height - count, height):
            if output[row][column] != background:
                raise Undefined("histogram columns collide")
            output[row][column] = color
    return tuple(tuple(row) for row in output)


def _read_histogram_mapping(source: Grid, target: Grid) -> tuple[int, int, dict[int, int]] | None:
    try:
        background = _strict_mode(source)
        target_background = _strict_mode(target)
    except Undefined:
        return None
    if target_background != background:
        return None
    height, width = _shape(target)
    colors = sorted({cell for row in source for cell in row} - {background})
    if len(colors) < 2:
        return None
    counts = {color: len(_eight_components(source, color)) for color in colors}
    if height != max(counts.values()):
        return None
    mapping: dict[int, int] = {}
    for color in colors:
        cells = [(row, column) for row in range(height) for column in range(width) if target[row][column] == color]
        if len(cells) != counts[color]:
            return None
        columns = {column for _, column in cells}
        if len(columns) != 1:
            return None
        column = next(iter(columns))
        if {row for row, _ in cells} != set(range(height - counts[color], height)):
            return None
        mapping[color] = column
    if any(cell not in set(colors) | {background} for row in target for cell in row):
        return None
    return background, width, mapping


def _learn_component_histogram(train: Sequence[Pair]) -> dict[str, Any] | None:
    background: int | None = None
    width: int | None = None
    mapping: dict[int, int] = {}
    for source, target in train:
        learned = _read_histogram_mapping(source, target)
        if learned is None:
            return None
        current_background, current_width, current_mapping = learned
        if background is None:
            background, width = current_background, current_width
        elif background != current_background or width != current_width:
            return None
        for color, column in current_mapping.items():
            if color in mapping and mapping[color] != column:
                return None
            mapping[color] = column
    if background is None or width is None or len(mapping) < 4 or len(set(mapping.values())) != len(mapping):
        return None
    program = {
        "schema": SCHEMA,
        "operator": "component_histogram",
        "background": background,
        "width": width,
        "column_by_color": [[color, mapping[color]] for color in sorted(mapping)],
        "connectivity": 8,
        "alignment": "bottom",
        "description_length": 18 + len(mapping),
    }
    try:
        return program if all(_execute_component_histogram(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _full_lines(value: Grid, color: int, *, rows: bool) -> tuple[int, ...]:
    height, width = _shape(value)
    if rows:
        return tuple(row for row in range(height) if all(value[row][column] == color for column in range(width)))
    return tuple(column for column in range(width) if all(value[row][column] == color for row in range(height)))


def _bands(length: int, separators: Sequence[int]) -> tuple[tuple[int, int], ...]:
    cuts = sorted(set(int(index) for index in separators))
    result: list[tuple[int, int]] = []
    start = 0
    for cut in cuts:
        if start < cut:
            result.append((start, cut - 1))
        start = cut + 1
    if start < length:
        result.append((start, length - 1))
    return tuple(result)


def _band_index(index: int, bands: Sequence[tuple[int, int]]) -> int:
    matches = [offset for offset, (low, high) in enumerate(bands) if low <= index <= high]
    if len(matches) != 1:
        raise Undefined("cell lies on or outside a panel band")
    return matches[0]


def _scaffold(value: Grid, fill: int, token: int) -> tuple[int, int, Cell]:
    height, width = _shape(value)
    candidates: list[tuple[int, int, Cell]] = []
    for top in range(height - 2):
        for left in range(width - 2):
            cells = [(row, column) for row in range(top, top + 3) for column in range(left, left + 3)]
            if all(value[row][column] in {fill, token} for row, column in cells):
                tokens = [(row, column) for row, column in cells if value[row][column] == token]
                if len(tokens) == 1:
                    candidates.append((top, left, tokens[0]))
    if len(candidates) != 1:
        raise Undefined("the three-by-three token scaffold is ambiguous")
    return candidates[0]


def _execute_panel_cue(value: Grid, program: Mapping[str, Any]) -> Grid:
    separator = int(program["separator"])
    fill = int(program["fill"])
    token = int(program["token"])
    cue = int(program["cue"])
    height, width = _shape(value)
    separator_rows = _full_lines(value, separator, rows=True)
    separator_columns = _full_lines(value, separator, rows=False)
    row_bands = _bands(height, separator_rows)
    column_bands = _bands(width, separator_columns)
    if len(separator_rows) < 2 or len(separator_columns) < 2 or len(row_bands) != 3 or len(column_bands) != 3:
        raise Undefined("a three-by-three panel layout is required")
    top, left, old_token = _scaffold(value, fill, token)
    cues = [(row, column) for row in range(height) for column in range(width) if value[row][column] == cue]
    if len(cues) != 1:
        raise Undefined("the directional cue must be unique")
    cue_cell = cues[0]
    scaffold_row_band = _band_index(top + 1, row_bands)
    scaffold_column_band = _band_index(left + 1, column_bands)
    cue_row_band = _band_index(cue_cell[0], row_bands)
    cue_column_band = _band_index(cue_cell[1], column_bands)
    local_row = 1 + cue_row_band - scaffold_row_band
    local_column = 1 + cue_column_band - scaffold_column_band
    if not (0 <= local_row < 3 and 0 <= local_column < 3):
        raise Undefined("cue direction exits the scaffold")
    destination = (top + local_row, left + local_column)
    if destination == old_token or value[destination[0]][destination[1]] != fill:
        raise Undefined("cue does not select a new scaffold cell")
    output = [list(row) for row in value]
    output[old_token[0]][old_token[1]] = fill
    output[destination[0]][destination[1]] = token
    output[cue_cell[0]][cue_cell[1]] = token
    return tuple(tuple(row) for row in output)


def _learn_panel_cue(train: Sequence[Pair]) -> dict[str, Any] | None:
    transition_sets: list[Counter[tuple[int, int]]] = []
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        transitions = Counter(
            (before, after)
            for source_row, target_row in zip(source, target)
            for before, after in zip(source_row, target_row)
            if before != after
        )
        transition_sets.append(transitions)
    triples: set[tuple[int, int, int]] = set()
    for cue in range(10):
        for token in range(10):
            for fill in range(10):
                if len({cue, token, fill}) != 3:
                    continue
                expected = Counter({(cue, token): 1, (token, fill): 1, (fill, token): 1})
                if all(transitions == expected for transitions in transition_sets):
                    triples.add((cue, token, fill))
    if len(triples) != 1:
        return None
    cue, token, fill = next(iter(triples))
    separators: set[int] | None = None
    for source, _ in train:
        current = {
            color
            for color in range(10)
            if len(_full_lines(source, color, rows=True)) >= 2
            and len(_full_lines(source, color, rows=False)) >= 2
        }
        separators = current if separators is None else separators & current
    if separators is None or len(separators) != 1:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "panel_cue",
        "separator": next(iter(separators)),
        "fill": fill,
        "token": token,
        "cue": cue,
        "panel_layout": [3, 3],
        "description_length": 20,
    }
    try:
        return program if all(_execute_panel_cue(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute_exemplar_stamp(value: Grid, program: Mapping[str, Any]) -> Grid:
    background = int(program["background"])
    marker = int(program["marker"])
    if _strict_mode(value) != background:
        raise Undefined("stamp background changed")
    height, width = _shape(value)
    marker_cells = [(row, column) for row in range(height) for column in range(width) if value[row][column] == marker]
    if not 4 <= len(marker_cells) <= 8:
        raise Undefined("exemplar marker count is outside the finite contract")
    top = min(row for row, _ in marker_cells)
    bottom = max(row for row, _ in marker_cells)
    left = min(column for _, column in marker_cells)
    right = max(column for _, column in marker_cells)
    if (bottom - top + 1, right - left + 1) != (3, 3):
        raise Undefined("marker cells do not define one three-by-three exemplar")
    template = tuple(tuple(value[row][column] for column in range(left, right + 1)) for row in range(top, bottom + 1))
    if sum(cell == marker for row in template for cell in row) != len(marker_cells):
        raise Undefined("marker cells occur outside the exemplar")
    matches: list[Cell] = []
    for candidate_top in range(height - 2):
        for candidate_left in range(width - 2):
            valid = True
            for local_row in range(3):
                for local_column in range(3):
                    expected = template[local_row][local_column]
                    observed = value[candidate_top + local_row][candidate_left + local_column]
                    if expected == marker:
                        if observed not in {background, marker}:
                            valid = False
                    elif observed != expected:
                        valid = False
            if valid:
                matches.append((candidate_top, candidate_left))
    if len(matches) < 2 or (top, left) not in matches:
        raise Undefined("the exemplar has no additional exact wildcard match")
    output = [list(row) for row in value]
    writes = 0
    for candidate_top, candidate_left in matches:
        for local_row in range(3):
            for local_column in range(3):
                if template[local_row][local_column] != marker:
                    continue
                row, column = candidate_top + local_row, candidate_left + local_column
                if output[row][column] == background:
                    output[row][column] = marker
                    writes += 1
    if writes < 1:
        raise Undefined("stamp makes no new marks")
    return tuple(tuple(row) for row in output)


def _learn_exemplar_stamp(train: Sequence[Pair]) -> dict[str, Any] | None:
    background: int | None = None
    marker: int | None = None
    for source, target in train:
        if _shape(source) != _shape(target):
            return None
        try:
            current_background = _strict_mode(source)
        except Undefined:
            return None
        transitions = Counter(
            (before, after)
            for source_row, target_row in zip(source, target)
            for before, after in zip(source_row, target_row)
            if before != after
        )
        if len(transitions) != 1:
            return None
        (before, after), count = next(iter(transitions.items()))
        if before != current_background or after == current_background or count < 1:
            return None
        if background is None:
            background, marker = current_background, after
        elif background != current_background or marker != after:
            return None
    if background is None or marker is None:
        return None
    program = {
        "schema": SCHEMA,
        "operator": "exemplar_stamp",
        "background": background,
        "marker": marker,
        "template_shape": [3, 3],
        "description_length": 17,
    }
    try:
        return program if all(_execute_exemplar_stamp(source, program) == target for source, target in train) else None
    except Undefined:
        return None


def _execute(program: Mapping[str, Any], value: Grid) -> Grid:
    if program.get("schema") != SCHEMA:
        raise Undefined("unknown program schema")
    operator = program.get("operator")
    if operator == "component_histogram":
        return _execute_component_histogram(value, program)
    if operator == "panel_cue":
        return _execute_panel_cue(value, program)
    if operator == "exemplar_stamp":
        return _execute_exemplar_stamp(value, program)
    raise Undefined("unknown selector/glyph operator")


def _programs(train: Sequence[Pair]) -> list[dict[str, Any]]:
    programs: list[dict[str, Any]] = []
    for learner in (_learn_component_histogram, _learn_panel_cue, _learn_exemplar_stamp):
        program = learner(train)
        if program is not None:
            programs.append(program)
    return programs


def execute_program(program: Mapping[str, Any], value: Any) -> list[list[int]]:
    """Execute one serialized task-local program."""

    return _plain(_execute(program, _grid(value)))


def replay_program(program: Mapping[str, Any], value: Any) -> dict[str, Any]:
    source = _grid(value)
    lifted = {
        "kind": "selector_glyph_scene",
        "shape": list(_shape(source)),
        "operator": program.get("operator"),
    }
    output = _execute(program, source)
    return {
        "output": _plain(output),
        "stages": [
            {"name": "lift-selector-glyph-scene", "input": _plain(source), "output": lifted},
            {"name": "execute-selector-glyph-schema", "input": lifted, "output": _plain(output)},
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
    operator = str(program["operator"])
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
        "family": "selector_glyph_compiler",
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
