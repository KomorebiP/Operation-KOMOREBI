"""Bounded local and periodic completion programs for ARC grids.

The standalone grammar contains two task-identifier-free typed schemas:

* complete every monochrome 2x2 L-triomino at its missing corner with one
  unanimous demonstration-inferred paint colour; and
* restore anomalous marker cells in a repeated period-5 lattice and stamp the
  marker colour into the source-derived twelve-cell interior role.

Programs contain no task identifier, raster, absolute coordinate, component
colour, or test-derived value.  Compilation requires exact demonstration
replay, canonical minimum-description selection, and rediscovery of the same
program after every distinct nonidentity demonstration group is removed.
Ambiguous interpretations and finite resource overruns fail closed.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]

SCHEMA = "komorebi.arc.repeated-local-lattice-completion-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_repeated_local_lattice_completion"

L_TRIOMINO_MISSING_CORNER = "complete_2x2_l_triomino_missing_corner"
PERIOD5_MARKER_INTERIOR_STAMP = "stamp_period5_marker_interior_role"

_OPERATORS = (
    L_TRIOMINO_MISSING_CORNER,
    PERIOD5_MARKER_INTERIOR_STAMP,
)
_COMPLEXITIES = {
    L_TRIOMINO_MISSING_CORNER: 15,
    PERIOD5_MARKER_INTERIOR_STAMP: 23,
}
_PERIOD = 5
_MARKER_CORNERS = (
    "northwest_corner_of_unit",
    "northeast_corner_of_unit",
    "southwest_corner_of_unit",
    "southeast_corner_of_unit",
)
_CORNER_SIGNS = {
    "northwest_corner_of_unit": (1, 1),
    "northeast_corner_of_unit": (1, -1),
    "southwest_corner_of_unit": (-1, 1),
    "southeast_corner_of_unit": (-1, -1),
}


class RepeatedLocalLatticeCompletionError(ValueError):
    """Base class for malformed programs and source rasters."""


class RepeatedLocalLatticeCompletionAbstention(
    RepeatedLocalLatticeCompletionError
):
    """Raised when a source has no unique supported interpretation."""


class RepeatedLocalLatticeCompletionAmbiguityError(
    RepeatedLocalLatticeCompletionAbstention
):
    """Raised when exact programs predict different held-out behaviors."""


class RepeatedLocalLatticeCompletionLimitError(
    RepeatedLocalLatticeCompletionError
):
    """Raised before a configured finite budget is exceeded."""


@dataclass(frozen=True)
class RepeatedLocalLatticeCompletionLimits:
    """Hard representation and execution budgets."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_components: int = 256
    maximum_triominoes: int = 128
    maximum_markers: int = 128
    maximum_writes: int = 900
    maximum_examples: int = 10
    maximum_tests: int = 8
    maximum_programs: int = 5
    maximum_candidates: int = 5
    minimum_phase_support: int = 3
    minimum_lattice_extent: int = 16

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise RepeatedLocalLatticeCompletionLimitError(
                    f"{name} must be a positive integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = RepeatedLocalLatticeCompletionLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def repeated_local_lattice_completion_implementation_fingerprint() -> str:
    """Hash the exact standalone compiler and interpreter source."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class RepeatedLocalLatticeCompletionProgram:
    """Canonical typed program with at most one learned palette value."""

    operator: str
    paint_color: Optional[int] = None
    marker_corner: Optional[str] = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, (int, np.integer))
            or int(self.schema_version) != SCHEMA_VERSION
        ):
            raise RepeatedLocalLatticeCompletionError(
                f"unsupported schema version {self.schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )
        object.__setattr__(self, "schema_version", int(self.schema_version))
        if self.operator not in _OPERATORS:
            raise RepeatedLocalLatticeCompletionError(
                f"unknown local/lattice operator {self.operator!r}"
            )
        if self.operator == L_TRIOMINO_MISSING_CORNER:
            if (
                isinstance(self.paint_color, bool)
                or not isinstance(self.paint_color, (int, np.integer))
                or not 0 <= int(self.paint_color) <= 9
            ):
                raise RepeatedLocalLatticeCompletionError(
                    "L-triomino completion requires one ARC paint colour"
                )
            object.__setattr__(self, "paint_color", int(self.paint_color))
            if self.marker_corner is not None:
                raise RepeatedLocalLatticeCompletionError(
                    "L-triomino programs do not carry a marker corner"
                )
        else:
            if self.paint_color is not None:
                raise RepeatedLocalLatticeCompletionError(
                    "periodic marker programs derive paint colours from the source"
                )
            if self.marker_corner not in _MARKER_CORNERS:
                raise RepeatedLocalLatticeCompletionError(
                    "periodic marker programs require one typed corner relation"
                )

    @classmethod
    def l_triomino_missing_corner(
        cls,
        paint_color: int,
    ) -> "RepeatedLocalLatticeCompletionProgram":
        return cls(L_TRIOMINO_MISSING_CORNER, paint_color=paint_color)

    @classmethod
    def period5_marker_interior_stamp(
        cls,
        marker_corner: str,
    ) -> "RepeatedLocalLatticeCompletionProgram":
        return cls(
            PERIOD5_MARKER_INTERIOR_STAMP,
            marker_corner=marker_corner,
        )

    @classmethod
    def from_record(
        cls,
        raw: object,
    ) -> "RepeatedLocalLatticeCompletionProgram":
        if not isinstance(raw, Mapping):
            raise RepeatedLocalLatticeCompletionError(
                "local/lattice program must be a mapping"
            )
        expected = {
            "schema",
            "schema_version",
            "operator",
            "paint_color",
            "marker_corner",
        }
        present = set(raw)
        if present != expected:
            raise RepeatedLocalLatticeCompletionError(
                "local/lattice program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise RepeatedLocalLatticeCompletionError(
                f"unknown local/lattice schema {raw['schema']!r}"
            )
        operator = raw["operator"]
        schema_version = raw["schema_version"]
        paint_color = raw["paint_color"]
        marker_corner = raw["marker_corner"]
        if not isinstance(operator, str):
            raise RepeatedLocalLatticeCompletionError(
                "program operator must be a string"
            )
        return cls(
            operator=operator,
            paint_color=paint_color,
            marker_corner=marker_corner,
            schema_version=schema_version,
        )

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
            "paint_color": (
                None if self.paint_color is None else int(self.paint_color)
            ),
            "marker_corner": self.marker_corner,
        }
        _canonical_json(record)
        return record

    @property
    def semantic_key(self) -> str:
        return _canonical_json(self.to_record())

    def program_hash(self) -> str:
        return hashlib.sha256(self.semantic_key.encode("ascii")).hexdigest()

    def content_hash(self) -> str:
        return self.program_hash()

    @property
    def complexity(self) -> int:
        return int(_COMPLEXITIES[self.operator])

    def apply(
        self,
        grid: Array,
        *,
        limits: RepeatedLocalLatticeCompletionLimits = DEFAULT_LIMITS,
    ) -> Array:
        output, _ = _execute_with_trace(self, grid, limits)
        return output


@dataclass(frozen=True)
class RepeatedLocalLatticeCompletionCandidate:
    """Entry-independent exact candidate with canonical provenance."""

    name: str
    program: RepeatedLocalLatticeCompletionProgram
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    complexity: int
    metadata: Mapping[str, object]
    family: str = FAMILY
    train_error: int = 0

    def to_record(self, *, include_grids: bool = True) -> Dict[str, object]:
        record: Dict[str, object] = {
            "name": str(self.name),
            "family": str(self.family),
            "train_error": int(self.train_error),
            "complexity": int(self.complexity),
            "program": self.program.to_record(),
            "metadata": dict(self.metadata),
        }
        if include_grids:
            record["grids"] = [grid.astype(int).tolist() for grid in self.grids]
            record["train_grids"] = [
                grid.astype(int).tolist() for grid in self.train_grids
            ]
        _canonical_json(record)
        return record


def _validated_grid(
    grid: Array,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise RepeatedLocalLatticeCompletionAbstention(
            "grid must be a nonempty matrix"
        )
    if not np.issubdtype(raw.dtype, np.integer):
        raise RepeatedLocalLatticeCompletionAbstention(
            "grid values must be integers"
        )
    values = np.asarray(raw, dtype=np.int64)
    height, width = values.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or values.size > limits.maximum_cells
    ):
        raise RepeatedLocalLatticeCompletionLimitError(
            "grid exceeds ARC representation limits"
        )
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise RepeatedLocalLatticeCompletionLimitError(
            "palette exceeds representation limit"
        )
    if np.any(palette < 0) or np.any(palette > 9):
        raise RepeatedLocalLatticeCompletionAbstention(
            "grid colours must lie in the ARC palette"
        )
    return np.ascontiguousarray(values.astype(np.int16))


def _unique_mode(grid: Array) -> int:
    colors, counts = np.unique(grid, return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        raise RepeatedLocalLatticeCompletionAmbiguityError(
            "background mode is tied"
        )
    return int(winners[0])


def _components(
    grid: Array,
    color: int,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Tuple[Tuple[Cell, ...], ...]:
    height, width = grid.shape
    remaining = {
        (int(row), int(column))
        for row, column in np.argwhere(grid == color)
    }
    components = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        stack = [seed]
        cells = []
        while stack:
            row, column = stack.pop()
            cells.append((row, column))
            for delta_row, delta_column in (
                (-1, 0),
                (0, -1),
                (0, 1),
                (1, 0),
            ):
                neighbor = (row + delta_row, column + delta_column)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(tuple(sorted(cells)))
        if len(components) > limits.maximum_components:
            raise RepeatedLocalLatticeCompletionLimitError(
                "component budget exceeded"
            )
    return tuple(components)


def _execute_l_triomino(
    program: RepeatedLocalLatticeCompletionProgram,
    source: Array,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Tuple[Array, Dict[str, object]]:
    background = _unique_mode(source)
    foreground = sorted(
        int(color) for color in np.unique(source) if int(color) != background
    )
    if len(foreground) != 1:
        raise RepeatedLocalLatticeCompletionAbstention(
            "L-triomino completion requires one foreground role"
        )
    paint_color = int(program.paint_color)  # validated by the program
    if paint_color in {background, foreground[0]} or np.any(source == paint_color):
        raise RepeatedLocalLatticeCompletionAbstention(
            "paint colour must be novel in the source"
        )
    components = _components(source, foreground[0], limits)
    if not 2 <= len(components) <= limits.maximum_triominoes:
        raise RepeatedLocalLatticeCompletionAbstention(
            "expected at least two bounded L-triomino witnesses"
        )
    writes = []
    roles = []
    for cells in components:
        if len(cells) != 3:
            raise RepeatedLocalLatticeCompletionAbstention(
                "foreground component is not a triomino"
            )
        rows = [cell[0] for cell in cells]
        columns = [cell[1] for cell in cells]
        top, bottom = min(rows), max(rows)
        left, right = min(columns), max(columns)
        if bottom - top != 1 or right - left != 1:
            raise RepeatedLocalLatticeCompletionAbstention(
                "triomino does not occupy an exact 2x2 box"
            )
        box = {
            (top, left),
            (top, right),
            (bottom, left),
            (bottom, right),
        }
        missing = box - set(cells)
        if len(missing) != 1:
            raise RepeatedLocalLatticeCompletionAbstention(
                "2x2 component has no unique missing corner"
            )
        cell = next(iter(missing))
        if int(source[cell]) != background:
            raise RepeatedLocalLatticeCompletionAbstention(
                "missing corner is not background"
            )
        writes.append(cell)
        row_role = "north" if cell[0] == top else "south"
        column_role = "west" if cell[1] == left else "east"
        roles.append(f"{row_role}_{column_role}")
    if len(set(writes)) != len(writes):
        raise RepeatedLocalLatticeCompletionAmbiguityError(
            "L-triomino completion writes collide"
        )
    if len(writes) > limits.maximum_writes:
        raise RepeatedLocalLatticeCompletionLimitError("write budget exceeded")
    if len(set(roles)) < 2:
        raise RepeatedLocalLatticeCompletionAbstention(
            "L-triomino source needs multiple missing-corner roles"
        )
    output = source.copy()
    for row, column in writes:
        output[row, column] = paint_color
    return output, {
        "operator": L_TRIOMINO_MISSING_CORNER,
        "background_color": int(background),
        "foreground_color_count": 1,
        "triomino_count": int(len(components)),
        "missing_corner_roles": sorted(set(roles)),
        "write_count": int(len(writes)),
        "paint_color_source_absent": True,
    }


def _phase_template(
    source: Array,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Tuple[Array, Tuple[int, int], Tuple[Cell, ...], int]:
    height, width = source.shape
    if (
        height < limits.minimum_lattice_extent
        or width < limits.minimum_lattice_extent
    ):
        raise RepeatedLocalLatticeCompletionAbstention(
            "period-5 lattice needs at least three repeated cells per axis"
        )
    template = np.zeros((_PERIOD, _PERIOD), dtype=np.int16)
    phase_support: Dict[Cell, int] = {}
    deviations: Dict[Cell, list[Cell]] = defaultdict(list)
    for row_phase in range(_PERIOD):
        for column_phase in range(_PERIOD):
            cells = [
                int(source[row, column])
                for row in range(row_phase, height, _PERIOD)
                for column in range(column_phase, width, _PERIOD)
            ]
            counts = Counter(cells)
            maximum = max(counts.values())
            winners = sorted(
                color for color, count in counts.items() if count == maximum
            )
            if len(winners) != 1 or maximum < limits.minimum_phase_support:
                raise RepeatedLocalLatticeCompletionAmbiguityError(
                    "periodic phase has no unique supported value"
                )
            value = int(winners[0])
            template[row_phase, column_phase] = value
            phase_support[(row_phase, column_phase)] = int(maximum)
            for row in range(row_phase, height, _PERIOD):
                for column in range(column_phase, width, _PERIOD):
                    if int(source[row, column]) != value:
                        deviations[(row_phase, column_phase)].append(
                            (row, column)
                        )
    active_phases = [phase for phase, cells in deviations.items() if cells]
    if len(active_phases) != 1:
        raise RepeatedLocalLatticeCompletionAbstention(
            "markers must be the only deviations and share one lattice phase"
        )
    trigger_phase = active_phases[0]
    markers = tuple(sorted(deviations[trigger_phase]))
    if not markers:
        raise RepeatedLocalLatticeCompletionAbstention(
            "periodic lattice contains no markers"
        )
    if len(markers) > limits.maximum_markers:
        raise RepeatedLocalLatticeCompletionLimitError(
            "marker budget exceeded"
        )
    return (
        template,
        trigger_phase,
        markers,
        min(phase_support.values()),
    )


def _contiguous_run(values: Iterable[int]) -> Optional[Tuple[int, ...]]:
    ordered = tuple(sorted(int(value) for value in values))
    if not ordered:
        return None
    if ordered != tuple(range(ordered[0], ordered[-1] + 1)):
        return None
    return ordered


def _lattice_stamp_offsets(
    template: Array,
    trigger_phase: Cell,
    marker_corner: str,
) -> Tuple[Cell, ...]:
    trigger_row, trigger_column = trigger_phase
    row_sign, column_sign = _CORNER_SIGNS[marker_corner]
    local = np.asarray(
        [
            [
                template[
                    (trigger_row + row_sign * row) % _PERIOD,
                    (trigger_column + column_sign * column) % _PERIOD,
                ]
                for column in range(_PERIOD)
            ]
            for row in range(_PERIOD)
        ],
        dtype=np.int16,
    )
    palette = sorted(int(color) for color in np.unique(local))
    if len(palette) != 2:
        raise RepeatedLocalLatticeCompletionAbstention(
            "periodic cell must contain exactly two structural colours"
        )
    interior_color = int(local[0, 0])
    row_zero = tuple(
        column
        for column in range(_PERIOD)
        if int(local[0, column]) == interior_color
    )
    if row_zero != (0,):
        raise RepeatedLocalLatticeCompletionAbstention(
            "marker phase is not the unique cell-opening role"
        )
    runs = []
    for row in range(1, _PERIOD):
        run = _contiguous_run(
            column
            for column in range(1, _PERIOD)
            if int(local[row, column]) == interior_color
        )
        if run is None:
            raise RepeatedLocalLatticeCompletionAbstention(
                "lattice interior is not a contiguous row role"
            )
        if any(
            int(local[row, column]) == interior_color
            for column in range(_PERIOD)
            if column not in run
        ):
            raise RepeatedLocalLatticeCompletionAbstention(
                "lattice interior has unsupported cells"
            )
        runs.append(run)
    if not (
        runs[0] == runs[3]
        and runs[1] == runs[2]
        and sorted(len(run) for run in runs) == [2, 2, 4, 4]
    ):
        raise RepeatedLocalLatticeCompletionAbstention(
            "lattice cell lacks the symmetric 2/4/4/2 interior profile"
        )
    short = runs[0] if len(runs[0]) == 2 else runs[1]
    long = runs[0] if len(runs[0]) == 4 else runs[1]
    if not set(short) < set(long) or len(set(long) - set(short)) != 2:
        raise RepeatedLocalLatticeCompletionAbstention(
            "lattice interior roles are not nested"
        )
    if tuple(long) != tuple(range(1, _PERIOD)):
        raise RepeatedLocalLatticeCompletionAbstention(
            "wide lattice interior does not span the bounded cell"
        )
    offsets = {
        (row, column)
        for row, run in enumerate(runs, start=1)
        for column in run
    }
    if len(offsets) != 12:
        raise RepeatedLocalLatticeCompletionAbstention(
            "lattice interior role is not twelve cells"
        )
    return tuple(
        sorted(
            (row_sign * row, column_sign * column)
            for row, column in offsets
        )
    )


def _execute_lattice_stamp(
    program: RepeatedLocalLatticeCompletionProgram,
    source: Array,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Tuple[Array, Dict[str, object]]:
    template, trigger_phase, markers, minimum_support = _phase_template(
        source,
        limits,
    )
    marker_corner = str(program.marker_corner)
    offsets = _lattice_stamp_offsets(
        template,
        trigger_phase,
        marker_corner,
    )
    height, width = source.shape
    desired: Dict[Cell, int] = {}
    trigger_value = int(template[trigger_phase])
    marker_colors = []
    for row, column in markers:
        marker_color = int(source[row, column])
        if marker_color == trigger_value:
            raise RepeatedLocalLatticeCompletionAbstention(
                "marker equals the restored lattice value"
            )
        marker_colors.append(marker_color)
        writes = [((row, column), trigger_value)] + [
            ((row + delta_row, column + delta_column), marker_color)
            for delta_row, delta_column in offsets
        ]
        for cell, color in writes:
            write_row, write_column = cell
            if not (0 <= write_row < height and 0 <= write_column < width):
                raise RepeatedLocalLatticeCompletionAbstention(
                    "marker lacks a complete interior lattice cell"
                )
            previous = desired.get(cell)
            if previous is not None and previous != color:
                raise RepeatedLocalLatticeCompletionAmbiguityError(
                    "marker stamps request conflicting writes"
                )
            desired[cell] = color
    if len(markers) < 2 or len(set(marker_colors)) < 2:
        raise RepeatedLocalLatticeCompletionAbstention(
            "periodic completion needs multiple markers and marker colours"
        )
    if len(desired) > limits.maximum_writes:
        raise RepeatedLocalLatticeCompletionLimitError("write budget exceeded")
    output = source.copy()
    for (row, column), color in desired.items():
        output[row, column] = color
    return output, {
        "operator": PERIOD5_MARKER_INTERIOR_STAMP,
        "row_period": _PERIOD,
        "column_period": _PERIOD,
        "trigger_phase": [int(value) for value in trigger_phase],
        "marker_corner": marker_corner,
        "marker_count": int(len(markers)),
        "distinct_marker_color_count": int(len(set(marker_colors))),
        "stamp_cell_count": int(len(offsets)),
        "write_count": int(len(desired)),
        "minimum_phase_support": int(minimum_support),
        "source_derived_template": True,
    }


def _execute_with_trace(
    program: RepeatedLocalLatticeCompletionProgram,
    grid: Array,
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Tuple[Array, Dict[str, object]]:
    source = _validated_grid(grid, limits)
    if program.operator == L_TRIOMINO_MISSING_CORNER:
        return _execute_l_triomino(program, source, limits)
    if program.operator == PERIOD5_MARKER_INTERIOR_STAMP:
        return _execute_lattice_stamp(program, source, limits)
    raise RepeatedLocalLatticeCompletionError(
        f"unsupported operator {program.operator!r}"
    )


def execute_repeated_local_lattice_completion_program(
    program: RepeatedLocalLatticeCompletionProgram,
    grid: Array,
    *,
    limits: RepeatedLocalLatticeCompletionLimits = DEFAULT_LIMITS,
) -> Array:
    """Execute one validated typed program against a source raster."""

    if not isinstance(program, RepeatedLocalLatticeCompletionProgram):
        raise RepeatedLocalLatticeCompletionError(
            "program has the wrong runtime type"
        )
    return program.apply(grid, limits=limits)


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _behavior_hash(grids: Sequence[Array]) -> str:
    digest = hashlib.sha256()
    for grid in grids:
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _infer_l_triomino_program(
    train: Sequence[Tuple[Array, Array]],
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Optional[RepeatedLocalLatticeCompletionProgram]:
    paint_colors = set()
    for source, target in train:
        if source.shape != target.shape:
            return None
        changed = source != target
        if not np.any(changed):
            return None
        colors = {int(color) for color in target[changed]}
        if len(colors) != 1:
            return None
        paint_colors.update(colors)
    if len(paint_colors) != 1:
        return None
    program = RepeatedLocalLatticeCompletionProgram.l_triomino_missing_corner(
        next(iter(paint_colors))
    )
    try:
        predictions = tuple(
            program.apply(source, limits=limits) for source, _ in train
        )
    except RepeatedLocalLatticeCompletionAbstention:
        return None
    if not all(
        np.array_equal(prediction, target)
        for prediction, (_, target) in zip(predictions, train)
    ):
        return None
    return program


def _exact_programs(
    train: Sequence[Tuple[Array, Array]],
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Dict[str, Tuple[RepeatedLocalLatticeCompletionProgram, Tuple[Array, ...]]]:
    programs = []
    local = _infer_l_triomino_program(train, limits)
    if local is not None:
        programs.append(local)
    programs.extend(
        RepeatedLocalLatticeCompletionProgram.period5_marker_interior_stamp(
            marker_corner
        )
        for marker_corner in _MARKER_CORNERS
    )
    if len(programs) > limits.maximum_programs:
        raise RepeatedLocalLatticeCompletionLimitError(
            "program grammar exceeds its finite budget"
        )
    exact_programs = {}
    for program in programs:
        try:
            predictions = tuple(
                program.apply(source, limits=limits) for source, _ in train
            )
        except RepeatedLocalLatticeCompletionAbstention:
            continue
        if all(
            np.array_equal(prediction, target)
            for prediction, (_, target) in zip(predictions, train)
        ):
            exact_programs[program.program_hash()] = (program, predictions)
    return exact_programs


def _discover_program(
    train: Sequence[Tuple[Array, Array]],
    limits: RepeatedLocalLatticeCompletionLimits,
) -> Optional[Tuple[RepeatedLocalLatticeCompletionProgram, Tuple[Array, ...]]]:
    exact_programs = _exact_programs(train, limits)
    if not exact_programs:
        return None
    return min(
        exact_programs.values(),
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )


def compile_repeated_local_lattice_completion_programs(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: RepeatedLocalLatticeCompletionLimits = DEFAULT_LIMITS,
) -> Tuple[RepeatedLocalLatticeCompletionCandidate, ...]:
    """Compile one exact, group-LOO-stable local/lattice program."""

    if len(train) < 2 or not tests:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise RepeatedLocalLatticeCompletionLimitError(
            "example budget exceeded"
        )
    try:
        validated = tuple(
            (
                _validated_grid(source, limits),
                _validated_grid(target, limits),
            )
            for source, target in train
        )
        validated_tests = tuple(
            _validated_grid(test, limits) for test in tests
        )
    except RepeatedLocalLatticeCompletionAbstention:
        return ()
    if any(source.shape != target.shape for source, target in validated):
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        if np.array_equal(source, target):
            continue
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 2:
        return ()

    exact_programs = _exact_programs(validated, limits)
    if not exact_programs:
        return ()
    selected, train_predictions = min(
        exact_programs.values(),
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )
    selected_hash = selected.program_hash()

    test_behaviors: Dict[str, list[str]] = defaultdict(list)
    selected_predictions = None
    for program_hash, (program, _) in sorted(exact_programs.items()):
        try:
            predictions = tuple(
                program.apply(test, limits=limits) for test in validated_tests
            )
        except RepeatedLocalLatticeCompletionAbstention:
            return ()
        behavior = _behavior_hash(predictions)
        test_behaviors[behavior].append(program_hash)
        if program_hash == selected_hash:
            selected_predictions = predictions
    if len(test_behaviors) > limits.maximum_candidates:
        raise RepeatedLocalLatticeCompletionLimitError(
            "exact behavior-class budget exceeded"
        )
    if len(test_behaviors) != 1:
        raise RepeatedLocalLatticeCompletionAmbiguityError(
            "full-data-exact local/lattice programs disagree on tests"
        )
    if selected_predictions is None:
        return ()

    loo_hashes = []
    loo_exact = 0
    for held_indices in groups.values():
        excluded = set(held_indices)
        construction = tuple(
            pair
            for index, pair in enumerate(validated)
            if index not in excluded
        )
        rediscovered = _discover_program(construction, limits)
        if rediscovered is None:
            break
        fold_program = rediscovered[0]
        fold_hash = fold_program.program_hash()
        loo_hashes.append(fold_hash)
        if fold_hash != selected_hash:
            break
        try:
            exact_group = all(
                np.array_equal(
                    fold_program.apply(
                        validated[index][0],
                        limits=limits,
                    ),
                    validated[index][1],
                )
                for index in held_indices
            )
        except RepeatedLocalLatticeCompletionAbstention:
            break
        if not exact_group:
            break
        loo_exact += 1
    if loo_exact != len(groups):
        return ()

    traces = []
    for source, _ in validated:
        _, trace = _execute_with_trace(selected, source, limits)
        traces.append(trace)
    palette_equivariant = selected.operator == PERIOD5_MARKER_INTERIOR_STAMP
    d4_equivariant = selected.operator == L_TRIOMINO_MISSING_CORNER
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.repeated-local-lattice-completion-candidate.v1",
        "program": selected.to_record(),
        "program_hash": selected_hash,
        "semantic_key": selected.semantic_key,
        "operator": selected.operator,
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "raw_grid_free_program": True,
        "literal_coordinate_free_program": True,
        "component_color_free_program": True,
        "paint_color_binding": (
            "unanimous_novel_added_color"
            if selected.operator == L_TRIOMINO_MISSING_CORNER
            else "copy_each_source_marker_color"
        ),
        "paint_color_is_demonstration_inferred": bool(
            selected.operator == L_TRIOMINO_MISSING_CORNER
        ),
        "marker_corner": selected.marker_corner,
        "palette_equivariant": bool(palette_equivariant),
        "d4_equivariant": bool(d4_equivariant),
        "quarter_turn_equivariant": bool(d4_equivariant),
        "witness_protocol": (
            "leave_one_distinct_nonidentity_group_out_rediscovery"
        ),
        "discovery_protocol": (
            "canonical_minimum_description_exact_program"
        ),
        "distinct_witness_groups": int(len(groups)),
        "loo_exact_count": int(loo_exact),
        "loo_total_count": int(len(groups)),
        "loo_program_hashes": list(loo_hashes),
        "witness_reconstructible": True,
        "full_exact_program_count": int(len(exact_programs)),
        "exact_test_behavior_count": int(len(test_behaviors)),
        "training_trace_summary": traces,
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": (
            repeated_local_lattice_completion_implementation_fingerprint()
        ),
        "bounded_schema_count": int(len(_OPERATORS)),
        "bounded_program_count": int(1 + len(_MARKER_CORNERS)),
        "limits": limits.to_record(),
    }
    return (
        RepeatedLocalLatticeCompletionCandidate(
            name=(
                "repeated_local_lattice_completion:"
                f"{selected.operator}:{selected_hash[:12]}"
            ),
            program=selected,
            grids=tuple(
                np.ascontiguousarray(grid) for grid in selected_predictions
            ),
            train_grids=tuple(
                np.ascontiguousarray(grid) for grid in train_predictions
            ),
            complexity=selected.complexity,
            metadata=metadata,
        ),
    )


repeated_local_lattice_completion_candidates = (
    compile_repeated_local_lattice_completion_programs
)


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "L_TRIOMINO_MISSING_CORNER",
    "PERIOD5_MARKER_INTERIOR_STAMP",
    "RepeatedLocalLatticeCompletionAbstention",
    "RepeatedLocalLatticeCompletionAmbiguityError",
    "RepeatedLocalLatticeCompletionCandidate",
    "RepeatedLocalLatticeCompletionError",
    "RepeatedLocalLatticeCompletionLimitError",
    "RepeatedLocalLatticeCompletionLimits",
    "RepeatedLocalLatticeCompletionProgram",
    "compile_repeated_local_lattice_completion_programs",
    "execute_repeated_local_lattice_completion_program",
    "repeated_local_lattice_completion_candidates",
    "repeated_local_lattice_completion_implementation_fingerprint",
]
