"""Locked role-normalized separator-axis constructor for PR-LASM Block 12.

The selected rule fills all-background rows or columns which lie strictly
inside the foreground bounding box.  Its paint color must be the single color
introduced by every training target.  It is intentionally small: broader
cell-state tables and two-atom component rules produced no additional program
on the bounded development panels and are retained only as negative evidence.

Compilation reads training pairs and test inputs only, requires exact replay,
and verifies D4 and palette conjugacy before exposing a behavior.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]
D4 = ("identity", "rot90", "rot180", "rot270", "flip_h", "flip_v", "transpose", "anti_transpose")
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm_falsification.local_transition_program"
COMPILATION_SCHEMA = "komorebi.lasm_falsification.local_transition_compilation"


class Inapplicable(ValueError):
    """The finite constructor contract does not apply."""


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
    rows = []
    for row in value:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        cells = []
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC cell")
            cells.append(int(cell))
        rows.append(tuple(cells))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > 30 or len(result[0]) > 30:
        raise ValueError("grid exceeds ARC limits")
    return result


def modal_background(value: Grid) -> int:
    counts = Counter(cell for row in value for cell in row)
    maximum = max(counts.values())
    winners = [color for color, count in counts.items() if count == maximum]
    if len(winners) != 1:
        raise Inapplicable("modal background is tied")
    return winners[0]


def blank_internal_axes(value: Grid) -> tuple[tuple[str, int], ...]:
    background = modal_background(value)
    foreground = [(row, column) for row, line in enumerate(value) for column, cell in enumerate(line) if cell != background]
    if not foreground:
        raise Inapplicable("foreground is empty")
    min_row = min(row for row, _ in foreground)
    max_row = max(row for row, _ in foreground)
    min_column = min(column for _, column in foreground)
    max_column = max(column for _, column in foreground)
    axes = []
    for row in range(min_row + 1, max_row):
        if all(value[row][column] == background for column in range(len(value[0]))):
            axes.append(("row", row))
    for column in range(min_column + 1, max_column):
        if all(value[row][column] == background for row in range(len(value))):
            axes.append(("column", column))
    return tuple(axes)


@dataclass(frozen=True, slots=True)
class SeparatorAxisProgram:
    novel_color: int
    family: str = "blank_internal_axis"

    def __post_init__(self) -> None:
        if self.family != "blank_internal_axis":
            raise ValueError("family lies outside the locked grammar")
        if isinstance(self.novel_color, bool) or not isinstance(self.novel_color, int) or not 0 <= self.novel_color <= 9:
            raise ValueError("novel color lies outside the ARC palette")

    @property
    def program_id(self) -> str:
        return _digest(self.to_record(include_id=False))

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "family": self.family,
            "parameters": {"paint_role": "single_training_novel_color", "novel_color": self.novel_color},
            "cost": 4,
            "status": "provisional",
        }
        if include_id:
            record["program_id"] = self.program_id
        return record

    def execute(self, value: Any) -> Grid:
        source = grid(value)
        background = modal_background(source)
        axes = blank_internal_axes(source)
        output = [list(row) for row in source]
        for orientation, index in axes:
            if orientation == "row":
                for column in range(len(source[0])):
                    if output[index][column] == background:
                        output[index][column] = self.novel_color
            else:
                for row in range(len(source)):
                    if output[row][index] == background:
                        output[row][index] = self.novel_color
        return tuple(tuple(row) for row in output)


def transform(value: Grid, operation: str) -> Grid:
    if operation == "identity":
        return value
    if operation == "rot90":
        return tuple(tuple(value[len(value) - 1 - row][column] for row in range(len(value))) for column in range(len(value[0])))
    if operation == "rot180":
        return tuple(tuple(reversed(row)) for row in reversed(value))
    if operation == "rot270":
        return tuple(tuple(value[row][len(value[0]) - 1 - column] for row in range(len(value))) for column in range(len(value[0])))
    if operation == "flip_h":
        return tuple(tuple(reversed(row)) for row in value)
    if operation == "flip_v":
        return tuple(reversed(value))
    if operation == "transpose":
        return tuple(tuple(value[row][column] for row in range(len(value))) for column in range(len(value[0])))
    if operation == "anti_transpose":
        return transform(transform(transform(value, "transpose"), "flip_h"), "flip_v")
    raise ValueError("unknown D4 operation")


def _novel_color(pairs: Sequence[tuple[Grid, Grid]]) -> int:
    differences = [
        {cell for row in target for cell in row} - {cell for row in source for cell in row}
        for source, target in pairs
    ]
    colors = set().union(*differences)
    if len(colors) != 1 or any(difference != colors for difference in differences):
        raise Inapplicable("demonstrations do not introduce one shared color")
    return next(iter(colors))


def _palette_permutation(values: Iterable[Grid]) -> dict[int, int] | None:
    colors = sorted({cell for value in values for row in value for cell in row})
    if len(colors) < 2:
        return None
    left, right = colors[-2:]
    permutation = {color: color for color in range(10)}
    permutation[left], permutation[right] = right, left
    return permutation


def _recolor(value: Grid, permutation: Mapping[int, int]) -> Grid:
    return tuple(tuple(permutation[cell] for cell in row) for row in value)


@dataclass(frozen=True, slots=True)
class LocalTransitionCompilation:
    routed: bool
    complete: bool
    programs: tuple[SeparatorAxisProgram, ...]
    behaviors: tuple[tuple[Grid, ...], ...]
    stress_checks: int

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
            "behaviors": [{"behavior_hash": _digest(value), "predictions": value} for value in self.behaviors],
            "stress_checks": self.stress_checks,
        }
        record["content_hash"] = _digest(record)
        return record


def compile_local_transition(task: Mapping[str, Any]) -> LocalTransitionCompilation:
    training = task.get("train")
    tests = task.get("test")
    if not isinstance(training, Sequence) or len(training) < 2 or not isinstance(tests, Sequence) or not tests:
        return LocalTransitionCompilation(False, True, (), (), 0)
    try:
        pairs = tuple((grid(example["input"]), grid(example["output"])) for example in training)
        test_inputs = tuple(grid(example["input"]) for example in tests)
        if any((len(source), len(source[0])) != (len(target), len(target[0])) for source, target in pairs):
            return LocalTransitionCompilation(False, True, (), (), 0)
        novel = _novel_color(pairs)
        program = SeparatorAxisProgram(novel)
        if any(not blank_internal_axes(source) or program.execute(source) != target for source, target in pairs):
            return LocalTransitionCompilation(True, True, (), (), 0)
        predictions = tuple(program.execute(value) for value in test_inputs)
        checks = 0
        for operation in D4:
            checks += 1
            for source, target in pairs:
                if program.execute(transform(source, operation)) != transform(target, operation):
                    raise Inapplicable("D4 conjugacy failed")
            transformed_predictions = tuple(program.execute(transform(value, operation)) for value in test_inputs)
            if transformed_predictions != tuple(transform(value, operation) for value in predictions):
                raise Inapplicable("D4 test behavior failed")
        permutation = _palette_permutation([value for pair in pairs for value in pair] + list(test_inputs))
        if permutation is not None:
            checks += 1
            recolored = SeparatorAxisProgram(permutation[novel])
            if any(recolored.execute(_recolor(source, permutation)) != _recolor(target, permutation) for source, target in pairs):
                raise Inapplicable("palette conjugacy failed")
            if tuple(recolored.execute(_recolor(value, permutation)) for value in test_inputs) != tuple(_recolor(value, permutation) for value in predictions):
                raise Inapplicable("palette test behavior failed")
        return LocalTransitionCompilation(True, True, (program,), (predictions,), checks)
    except (Inapplicable, KeyError, TypeError, ValueError, IndexError):
        return LocalTransitionCompilation(True, True, (), (), 0)


GRAMMAR_HASH = _digest({
    "schema": "komorebi.lasm_falsification.local_transition_grammar",
    "schema_version": SCHEMA_VERSION,
    "families": ["blank_internal_axis"],
    "paint_role": "single_training_novel_color",
    "d4": D4,
    "palette_probe": "swap_two_largest_observed_colors",
})


__all__ = [
    "D4", "GRAMMAR_HASH", "Grid", "LocalTransitionCompilation",
    "SeparatorAxisProgram", "blank_internal_axes", "compile_local_transition",
    "grid", "modal_background", "transform",
]
