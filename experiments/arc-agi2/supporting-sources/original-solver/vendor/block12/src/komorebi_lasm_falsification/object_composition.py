"""Role-carrying object crop composition for PR-LASM Block 12.

The schema selects the unique largest 4-connected monochrome object, renders
its raw bounding crop, and recolors the unique largest 8-connected object in
that crop to the crop's unique rarest foreground color.  Crucially, the modal
background is inferred on the root grid and transported into the crop capsule;
it is never re-inferred after foreground-dominant cropping.

Compilation is task-ID-free, sanitizes attached test labels, requires exact
demonstration replay, and fail-closes on every tie or invalid input.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

from komorebi_lasm_composition.task import sanitized_task_mapping


Grid = tuple[tuple[int, ...], ...]
Cell = tuple[int, int]
ORTHOGONAL = ((-1, 0), (0, -1), (0, 1), (1, 0))
DIAGONAL = tuple(
    (dy, dx)
    for dy in (-1, 0, 1)
    for dx in (-1, 0, 1)
    if (dy, dx) != (0, 0)
)
D4 = ("id", "r90", "r180", "r270", "fliplr", "flipud", "transpose", "anti_transpose")
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm_falsification.object_composition_program"
COMPILATION_SCHEMA = "komorebi.lasm_falsification.object_composition_compilation"
FAMILY = "role_carried_largest_object_recolor_crop"


class Inapplicable(ValueError):
    """The locked object-composition contract does not apply."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("ascii")).hexdigest()


def grid(value: Any) -> Grid:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TypeError("grid must be a row sequence")
    if not 1 <= len(value) <= 30:
        raise ValueError("grid height lies outside ARC bounds")
    rows = []
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        if not 1 <= len(raw_row) <= 30:
            raise ValueError("grid width lies outside ARC bounds")
        row = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("ARC cells must be non-Boolean integers in [0, 9]")
            row.append(cell)
        rows.append(tuple(row))
    result = tuple(rows)
    if any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be rectangular")
    return result


def _modal_background(source: Grid) -> int:
    counts = Counter(cell for row in source for cell in row)
    maximum = max(counts.values())
    winners = tuple(color for color, count in counts.items() if count == maximum)
    if len(winners) != 1:
        raise Inapplicable("root modal background is tied")
    return winners[0]


def _components(cells: set[Cell], connectivity: int) -> tuple[frozenset[Cell], ...]:
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")
    directions = ORTHOGONAL if connectivity == 4 else DIAGONAL
    unseen = set(cells)
    answer = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        group = {seed}
        queue = deque((seed,))
        while queue:
            row, column = queue.popleft()
            for dy, dx in directions:
                candidate = row + dy, column + dx
                if candidate in unseen:
                    unseen.remove(candidate)
                    group.add(candidate)
                    queue.append(candidate)
        answer.append(frozenset(group))
    if not answer or len(answer) > 96:
        raise Inapplicable("component partition is empty or over budget")
    return tuple(sorted(answer, key=lambda component: min(component)))


def _monochrome_components(source: Grid, background: int, connectivity: int) -> tuple[frozenset[Cell], ...]:
    height, width = len(source), len(source[0])
    answer = []
    for color in sorted({cell for row in source for cell in row} - {background}):
        support = {
            (row, column)
            for row in range(height)
            for column in range(width)
            if source[row][column] == color
        }
        answer.extend(_components(support, connectivity))
    if not answer or len(answer) > 96:
        raise Inapplicable("monochrome partition is empty or over budget")
    return tuple(sorted(answer, key=lambda component: min(component)))


def _unique_largest(items: tuple[frozenset[Cell], ...]) -> frozenset[Cell]:
    maximum = max(map(len, items))
    winners = tuple(item for item in items if len(item) == maximum)
    if len(winners) != 1:
        raise Inapplicable("largest component is tied")
    return winners[0]


def _crop(source: Grid, cells: frozenset[Cell]) -> Grid:
    top = min(row for row, _ in cells)
    bottom = max(row for row, _ in cells)
    left = min(column for _, column in cells)
    right = max(column for _, column in cells)
    return tuple(
        tuple(source[row][column] for column in range(left, right + 1))
        for row in range(top, bottom + 1)
    )


def _transform(source: Grid, operation: str) -> Grid:
    if operation == "id":
        return source
    if operation == "fliplr":
        return tuple(tuple(reversed(row)) for row in source)
    if operation == "flipud":
        return tuple(reversed(source))
    if operation == "r180":
        return _transform(_transform(source, "fliplr"), "flipud")
    transposed = tuple(tuple(source[row][column] for row in range(len(source))) for column in range(len(source[0])))
    if operation == "transpose":
        return transposed
    if operation == "r90":
        return tuple(tuple(reversed(row)) for row in transposed)
    if operation == "r270":
        return tuple(reversed(transposed))
    if operation == "anti_transpose":
        return _transform(transposed, "r180")
    raise ValueError("unknown D4 operation")


def _recolor(source: Grid, permutation: Mapping[int, int]) -> Grid:
    return tuple(tuple(permutation.get(cell, cell) for cell in row) for row in source)


@dataclass(frozen=True, slots=True)
class RoleCarriedObjectProgram:
    family: str = FAMILY

    def __post_init__(self) -> None:
        if self.family != FAMILY:
            raise ValueError("family lies outside the locked grammar")

    @property
    def program_id(self) -> str:
        return _digest(self.to_record(include_id=False))

    def execute(self, value: Any) -> Grid:
        source = grid(value)
        background = _modal_background(source)
        outer = _unique_largest(_monochrome_components(source, background, 4))
        capsule = _crop(source, outer)
        inner = _unique_largest(_monochrome_components(capsule, background, 8))
        foreground = Counter(cell for row in capsule for cell in row if cell != background)
        if len(foreground) < 2:
            raise Inapplicable("crop has fewer than two foreground colors")
        minimum = min(foreground.values())
        paints = tuple(color for color, count in foreground.items() if count == minimum)
        if len(paints) != 1:
            raise Inapplicable("rarest crop foreground is tied")
        paint = paints[0]
        if all(capsule[row][column] == paint for row, column in inner):
            raise Inapplicable("inner action would be identity")
        output = [list(row) for row in capsule]
        for row, column in inner:
            output[row][column] = paint
        return tuple(tuple(row) for row in output)

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "family": self.family,
            "parameters": {
                "root_background": "unique_most_frequent",
                "outer_partition": "4_connected_monochrome_components",
                "outer_selector": "unique_largest_support",
                "outer_renderer": "raw_bounding_crop",
                "state_transport": ["root_background"],
                "inner_partition": "8_connected_monochrome_components",
                "inner_selector": "unique_largest_support",
                "paint_role": "unique_rarest_crop_foreground_by_pixels",
                "inner_action": "recolor_selected_support",
            },
            "input_type": "grid",
            "output_type": "grid",
            "cost": 7,
            "status": "provisional",
        }
        if include_id:
            record["program_id"] = self.program_id
        return record


PROGRAM = RoleCarriedObjectProgram()
GRAMMAR_HASH = _digest({
    "schema": "komorebi.lasm_falsification.object_composition_grammar",
    "schema_version": SCHEMA_VERSION,
    "program": PROGRAM.to_record(),
    "limits": {"grid_height": 30, "grid_width": 30, "components": 96},
    "gauge_generators": {"spatial": list(D4), "palette": [f"swap_{index}_{index + 1}" for index in range(9)]},
})


def _stress(program: RoleCarriedObjectProgram, sources: tuple[Grid, ...], outputs: tuple[Grid, ...]) -> int:
    checks = 0
    for source, expected in zip(sources, outputs, strict=True):
        for operation in D4:
            if program.execute(_transform(source, operation)) != _transform(expected, operation):
                raise Inapplicable("D4 covariance failed")
            checks += 1
        for left in range(9):
            permutation = {left: left + 1, left + 1: left}
            if program.execute(_recolor(source, permutation)) != _recolor(expected, permutation):
                raise Inapplicable("palette-generator covariance failed")
            checks += 1
    return checks


@dataclass(frozen=True, slots=True)
class ObjectCompositionCompilation:
    routed: bool
    complete: bool
    programs: tuple[RoleCarriedObjectProgram, ...]
    behaviors: tuple[tuple[Grid, ...], ...]
    stress_checks: int

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def status(self) -> str:
        if not self.routed:
            return "not_routed"
        if not self.complete:
            return "limit_abstention"
        if len(self.behaviors) > 1:
            return "ambiguous_abstention"
        return "unique" if self.behaviors else "no_candidate"

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "routed": self.routed,
            "complete": self.complete,
            "programs": [program.to_record() for program in self.programs],
            "behavior_count": len(self.behaviors),
            "behaviors": [
                {"behavior_hash": _digest(behavior), "predictions": behavior}
                for behavior in self.behaviors
            ],
            "stress_checks": self.stress_checks,
        }
        record["content_hash"] = _digest(record)
        return record


def compile_object_composition(task: Mapping[str, Any]) -> ObjectCompositionCompilation:
    try:
        safe = sanitized_task_mapping(task)
        training = tuple((grid(example["input"]), grid(example["output"])) for example in safe["train"])
        tests = tuple(grid(example["input"]) for example in safe["test"])
    except Exception:
        return ObjectCompositionCompilation(False, False, (), (), 0)
    if len(training) < 2 or not tests:
        return ObjectCompositionCompilation(False, True, (), (), 0)
    routed = any(
        (len(source), len(source[0])) != (len(target), len(target[0]))
        for source, target in training
    )
    if not routed:
        return ObjectCompositionCompilation(False, True, (), (), 0)
    try:
        training_outputs = tuple(PROGRAM.execute(source) for source, _ in training)
        if training_outputs != tuple(target for _, target in training):
            return ObjectCompositionCompilation(True, True, (), (), 0)
        predictions = tuple(PROGRAM.execute(source) for source in tests)
        sources = tuple(source for source, _ in training) + tests
        outputs = training_outputs + predictions
        stress_checks = _stress(PROGRAM, sources, outputs)
    except (Inapplicable, TypeError, ValueError, IndexError):
        return ObjectCompositionCompilation(True, True, (), (), 0)
    return ObjectCompositionCompilation(True, True, (PROGRAM,), (predictions,), stress_checks)


__all__ = [
    "COMPILATION_SCHEMA", "D4", "FAMILY", "GRAMMAR_HASH", "Grid", "Inapplicable",
    "ObjectCompositionCompilation", "PROGRAM", "PROGRAM_SCHEMA", "RoleCarriedObjectProgram",
    "compile_object_composition", "grid",
]
