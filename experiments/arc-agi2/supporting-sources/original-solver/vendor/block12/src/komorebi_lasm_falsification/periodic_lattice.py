"""Locked boundary-key periodic extension for PR-LASM Block 12.

The broader periodic/coordinate challenger was frozen and scored over all 471
eligible Block 11 same-shape misses.  Only this role-bound schema survived:
read a unique color key from the boundary immediately before one uniform
separator, then repeat that key as constant stripes across a blank canvas.

Compilation is task-ID-free, sanitizes test examples, exactly replays every
demonstration, enumerates all D4 charts, and quotients complete test behavior.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

from komorebi_lasm_composition.task import sanitized_task_mapping


Grid = tuple[tuple[int, ...], ...]
D4 = ("id", "r90", "r180", "r270", "fliplr", "flipud", "transpose", "anti_transpose")
INVERSE_D4 = {
    "id": "id", "r90": "r270", "r180": "r180", "r270": "r90",
    "fliplr": "fliplr", "flipud": "flipud", "transpose": "transpose",
    "anti_transpose": "anti_transpose",
}
COLOR_ROLES = (
    "zero", "mode", "corner_mode", "singleton", "rarest_nonzero",
    "most_frequent_nonzero",
)
SCHEMA_VERSION = 1
PROGRAM_SCHEMA = "komorebi.lasm_falsification.periodic_lattice_program"
COMPILATION_SCHEMA = "komorebi.lasm_falsification.periodic_lattice_compilation"


class Inapplicable(ValueError):
    """The locked boundary-key contract does not apply."""


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
    for raw_row in value:
        if not isinstance(raw_row, Sequence) or isinstance(raw_row, (str, bytes, bytearray)):
            raise TypeError("grid row must be a sequence")
        row = []
        for cell in raw_row:
            if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("invalid ARC cell")
            row.append(int(cell))
        rows.append(tuple(row))
    result = tuple(rows)
    if not result or not result[0] or any(len(row) != len(result[0]) for row in result):
        raise ValueError("grid must be nonempty and rectangular")
    if len(result) > 30 or len(result[0]) > 30:
        raise ValueError("grid exceeds ARC limits")
    return result


def transform(source: Grid, name: str) -> Grid:
    if name == "id":
        return source
    if name == "fliplr":
        return tuple(tuple(reversed(row)) for row in source)
    if name == "flipud":
        return tuple(reversed(source))
    if name == "r180":
        return transform(transform(source, "fliplr"), "flipud")
    transposed = tuple(tuple(source[y][x] for y in range(len(source))) for x in range(len(source[0])))
    if name == "transpose":
        return transposed
    if name == "r90":
        return tuple(tuple(reversed(row)) for row in transposed)
    if name == "r270":
        return tuple(reversed(transposed))
    if name == "anti_transpose":
        return transform(transposed, "r180")
    raise ValueError("unknown D4 chart")


def _unique_extreme(counts: Counter[int], *, largest: bool) -> int:
    if not counts:
        raise Inapplicable("empty color-role domain")
    extreme = (max if largest else min)(counts.values())
    matches = [color for color, count in counts.items() if count == extreme]
    if len(matches) != 1:
        raise Inapplicable("color role is tied")
    return matches[0]


def resolve_color_role(source: Grid, role: str) -> int:
    counts = Counter(cell for row in source for cell in row)
    if role == "zero":
        if 0 not in counts:
            raise Inapplicable("zero role is absent")
        return 0
    if role == "mode":
        return _unique_extreme(counts, largest=True)
    if role == "corner_mode":
        return _unique_extreme(Counter((source[0][0], source[0][-1], source[-1][0], source[-1][-1])), largest=True)
    if role == "singleton":
        matches = [color for color, count in counts.items() if count == 1]
        if len(matches) != 1:
            raise Inapplicable("singleton role is tied or absent")
        return matches[0]
    nonzero = Counter({color: count for color, count in counts.items() if color != 0})
    if role == "rarest_nonzero":
        return _unique_extreme(nonzero, largest=False)
    if role == "most_frequent_nonzero":
        return _unique_extreme(nonzero, largest=True)
    raise ValueError("unknown color role")


def execute_boundary_key(source: Grid, separator_role: str, background_role: str) -> Grid:
    separator = resolve_color_role(source, separator_role)
    background = resolve_color_role(source, background_role)
    if separator == background:
        raise Inapplicable("separator and background roles collapse")
    height, width = len(source), len(source[0])
    separator_rows = [row for row, values in enumerate(source) if all(cell == separator for cell in values)]
    if separator_rows != [1] or height - 2 < 2 * width:
        raise Inapplicable("one boundary separator and two full cycles are required")
    key = source[0]
    if width < 2 or len(set(key)) != width or any(cell in {separator, background} for cell in key):
        raise Inapplicable("boundary key is not a unique role sequence")
    if any(source[y][x] != background for y in range(2, height) for x in range(width)):
        raise Inapplicable("periodic extension canvas is not blank")
    output = [list(row) for row in source]
    for y in range(2, height):
        color = key[(y - 2) % width]
        output[y] = [color] * width
    return tuple(tuple(row) for row in output)


@dataclass(frozen=True, slots=True)
class BoundaryKeyProgram:
    gauge: str
    separator_role: str
    background_role: str
    family: str = "boundary_key_sequence_extension"

    def __post_init__(self) -> None:
        if self.gauge not in D4 or self.separator_role not in COLOR_ROLES or self.background_role not in COLOR_ROLES:
            raise ValueError("program parameter lies outside the frozen domain")
        if self.separator_role == self.background_role or self.family != "boundary_key_sequence_extension":
            raise ValueError("invalid boundary-key program")

    @property
    def program_id(self) -> str:
        return _digest(self.to_record(include_id=False))

    def execute(self, value: Any) -> Grid:
        source = transform(grid(value), self.gauge)
        output = execute_boundary_key(source, self.separator_role, self.background_role)
        return transform(output, INVERSE_D4[self.gauge])

    def to_record(self, *, include_id: bool = True) -> dict[str, Any]:
        record: dict[str, Any] = {
            "schema": PROGRAM_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "family": self.family,
            "parameters": {
                "gauge": self.gauge,
                "separator_role": self.separator_role,
                "background_role": self.background_role,
                "payload_role": "current_input_boundary_key",
            },
            "cost": 5,
            "status": "provisional",
        }
        if include_id:
            record["program_id"] = self.program_id
        return record


@dataclass(frozen=True, slots=True)
class PeriodicLatticeCompilation:
    routed: bool
    complete: bool
    programs: tuple[BoundaryKeyProgram, ...]
    behaviors: tuple[tuple[Grid, ...], ...]
    demonstration_executions: int
    runtime_failures: int

    @property
    def selected_prediction(self) -> tuple[Grid, ...] | None:
        return self.behaviors[0] if len(self.behaviors) == 1 else None

    @property
    def ambiguous(self) -> bool:
        return len(self.behaviors) > 1

    @property
    def status(self) -> str:
        if not self.routed:
            return "not_routed"
        if not self.complete:
            return "limit_abstention"
        if self.ambiguous:
            return "ambiguous_abstention"
        return "unique" if self.selected_prediction is not None else "no_candidate"

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "routed": self.routed,
            "complete": self.complete,
            "programs": [program.to_record() for program in self.programs],
            "behavior_count": len(self.behaviors),
            "behaviors": [{"behavior_hash": _digest(value), "predictions": value} for value in self.behaviors],
            "demonstration_executions": self.demonstration_executions,
            "runtime_failures": self.runtime_failures,
        }
        record["content_hash"] = _digest(record)
        return record


def compile_periodic_lattice(task: Mapping[str, Any]) -> PeriodicLatticeCompilation:
    try:
        safe = sanitized_task_mapping(task)
        training = safe["train"]
        tests = safe["test"]
        if len(training) < 2 or not tests:
            return PeriodicLatticeCompilation(False, True, (), (), 0, 0)
        pairs = tuple((grid(example["input"]), grid(example["output"])) for example in training)
        if any(len(source) != len(target) or len(source[0]) != len(target[0]) or source == target for source, target in pairs):
            return PeriodicLatticeCompilation(False, True, (), (), 0, 0)
        test_inputs = tuple(grid(example["input"]) for example in tests)
    except (KeyError, TypeError, ValueError):
        return PeriodicLatticeCompilation(False, True, (), (), 0, 0)

    exact = []
    executions = failures = 0
    for gauge in D4:
        for separator_role in COLOR_ROLES:
            for background_role in COLOR_ROLES:
                if separator_role == background_role:
                    continue
                program = BoundaryKeyProgram(gauge, separator_role, background_role)
                matched = True
                for source, target in pairs:
                    try:
                        observed = program.execute(source)
                        executions += 1
                    except (IndexError, TypeError, ValueError):
                        failures += 1
                        matched = False
                        break
                    if observed != target:
                        matched = False
                        break
                if matched:
                    exact.append(program)
    groups: dict[str, tuple[Grid, ...]] = {}
    survivors = []
    for program in exact:
        try:
            predictions = tuple(program.execute(source) for source in test_inputs)
        except (IndexError, TypeError, ValueError):
            failures += 1
            continue
        key = _digest(predictions)
        if key in groups and groups[key] != predictions:
            raise AssertionError("behavior hash collision")
        groups[key] = predictions
        survivors.append(program)
    behaviors = tuple(groups[key] for key in sorted(groups))
    return PeriodicLatticeCompilation(True, True, tuple(sorted(survivors, key=lambda value: value.program_id)), behaviors, executions, failures)


GRAMMAR_HASH = _digest({
    "schema": "komorebi.lasm_falsification.periodic_lattice_grammar",
    "schema_version": SCHEMA_VERSION,
    "families": ["boundary_key_sequence_extension"],
    "d4": D4,
    "color_roles": COLOR_ROLES,
    "minimum_demonstrations": 2,
    "minimum_complete_cycles": 2,
    "complete_behavior_quotient": True,
})


__all__ = [
    "BoundaryKeyProgram", "COLOR_ROLES", "D4", "GRAMMAR_HASH", "Grid",
    "PeriodicLatticeCompilation", "compile_periodic_lattice", "execute_boundary_key",
    "grid", "resolve_color_role", "transform",
]
