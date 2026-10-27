"""Typed outward-corner marking for filled and framed square components.

The fixed interpreter enumerates monochrome four-connected components, binds
every exact regular square, and paints the two outward cardinal neighbours of
each bounding-box corner.  A regular square is either a filled square or a
one-cell-thick square perimeter.  Non-square components are preserved as
distractors.  Marking is atomic and fail-closed: selected squares require a
complete one-cell background workspace, marker requests may not overlap, and
the demonstration-inferred paint colour must be absent from the source.

The compiler learns only that paint colour.  It requires exact replay, a
single unanimous added-colour witness, individual demonstration leave-one-out
reinduction, and distinct-group leave-one-out reinduction.  The persistent
program contains no raster, coordinate, task identifier, component colour, or
object size.  This module is intentionally independent of ``entry.py`` and
the previously audited role-bound interpreter.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]

SCHEMA = "komorebi.arc.regular-square-corner-mark-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_regular_square_corner_mark"
OPERATOR = "mark_regular_square_outward_corner_neighbors"


class RegularSquareCornerMarkError(ValueError):
    """Base class for invalid programs and explicit abstentions."""


class RegularSquareCornerMarkAbstention(RegularSquareCornerMarkError):
    """Raised when a source has no unique protected interpretation."""


class RegularSquareCornerMarkLimitError(RegularSquareCornerMarkError):
    """Raised before a finite representation budget is exceeded."""


@dataclass(frozen=True)
class RegularSquareCornerMarkLimits:
    """Hard bounds for the standalone compiler and interpreter."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_components: int = 128
    maximum_squares: int = 64
    maximum_marker_cells: int = 512
    maximum_examples: int = 10
    maximum_tests: int = 8

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise RegularSquareCornerMarkLimitError(
                    f"{name} must be a positive integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = RegularSquareCornerMarkLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def regular_square_corner_mark_implementation_fingerprint() -> str:
    """Hash the exact interpreter and compiler source."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class RegularSquareCornerMarkProgram:
    """Canonical typed program with one witnessed paint-colour parameter."""

    paint_color: int
    operator: str = OPERATOR
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise RegularSquareCornerMarkError(
                f"unsupported schema version {self.schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )
        if self.operator != OPERATOR:
            raise RegularSquareCornerMarkError(
                f"unknown regular-square operator {self.operator!r}"
            )
        if (
            isinstance(self.paint_color, bool)
            or not isinstance(self.paint_color, (int, np.integer))
            or not 0 <= int(self.paint_color) <= 9
        ):
            raise RegularSquareCornerMarkError(
                "paint_color must be one ARC palette integer"
            )
        object.__setattr__(self, "paint_color", int(self.paint_color))

    @classmethod
    def from_record(cls, raw: object) -> "RegularSquareCornerMarkProgram":
        if not isinstance(raw, Mapping):
            raise RegularSquareCornerMarkError(
                "regular-square program must be a mapping"
            )
        expected = {
            "schema",
            "schema_version",
            "operator",
            "paint_color",
        }
        present = set(raw)
        if present != expected:
            raise RegularSquareCornerMarkError(
                "regular-square program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise RegularSquareCornerMarkError(
                f"unknown regular-square schema {raw['schema']!r}"
            )
        return cls(
            paint_color=int(raw["paint_color"]),
            operator=str(raw["operator"]),
            schema_version=int(raw["schema_version"]),
        )

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
            "paint_color": int(self.paint_color),
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
        return 17

    def apply(
        self,
        grid: Array,
        *,
        limits: RegularSquareCornerMarkLimits = DEFAULT_LIMITS,
    ) -> Array:
        return execute_regular_square_corner_mark_program(
            self,
            grid,
            limits=limits,
        )


@dataclass(frozen=True)
class _Component:
    color: int
    cells: Tuple[Cell, ...]
    box: Box


@dataclass(frozen=True)
class _RegularSquare:
    kind: str
    side: int
    box: Box


@dataclass(frozen=True)
class RegularSquareCornerMarkTrace:
    """Coordinate-free runtime evidence for one source interpretation."""

    background_color: int
    component_count: int
    square_count: int
    filled_square_count: int
    framed_square_count: int
    distractor_component_count: int
    square_sides: Tuple[int, ...]
    marker_cell_count: int

    def to_record(self) -> Dict[str, object]:
        return {
            "background_color": int(self.background_color),
            "component_count": int(self.component_count),
            "square_count": int(self.square_count),
            "filled_square_count": int(self.filled_square_count),
            "framed_square_count": int(self.framed_square_count),
            "distractor_component_count": int(
                self.distractor_component_count
            ),
            "square_sides": [int(side) for side in self.square_sides],
            "marker_cell_count": int(self.marker_cell_count),
        }


@dataclass(frozen=True)
class PaintColorWitness:
    """Per-demonstration proof that one novel colour explains every edit."""

    paint_color: int
    background_color: int
    changed_cell_count: int
    source_palette_size: int
    target_palette_size: int

    def to_record(self) -> Dict[str, object]:
        return {
            "paint_color": int(self.paint_color),
            "background_color": int(self.background_color),
            "changed_cell_count": int(self.changed_cell_count),
            "source_palette_size": int(self.source_palette_size),
            "target_palette_size": int(self.target_palette_size),
            "all_changes_from_background": True,
            "single_added_color": True,
            "paint_color_absent_from_source": True,
        }


@dataclass(frozen=True)
class RegularSquareCornerMarkCandidate:
    """Entry-independent exact candidate with canonical program provenance."""

    name: str
    program: RegularSquareCornerMarkProgram
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
    limits: RegularSquareCornerMarkLimits,
) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise RegularSquareCornerMarkAbstention(
            "grid must be a nonempty matrix"
        )
    if not np.issubdtype(raw.dtype, np.integer):
        raise RegularSquareCornerMarkAbstention(
            "grid values must be integers"
        )
    values = np.asarray(raw, dtype=np.int64)
    height, width = values.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or values.size > limits.maximum_cells
    ):
        raise RegularSquareCornerMarkLimitError(
            "grid exceeds ARC representation limits"
        )
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise RegularSquareCornerMarkLimitError(
            "palette exceeds representation limit"
        )
    if np.any(palette < 0) or np.any(palette > 9):
        raise RegularSquareCornerMarkAbstention(
            "grid colors must lie in the ARC palette"
        )
    return values.copy()


def _background(source: Array) -> int:
    colors, counts = np.unique(source, return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        raise RegularSquareCornerMarkAbstention(
            "global background mode is not unique"
        )
    return int(winners[0])


def _components(
    source: Array,
    background: int,
    limits: RegularSquareCornerMarkLimits,
) -> Tuple[_Component, ...]:
    height, width = source.shape
    seen: set[Cell] = set()
    output = []
    for row in range(height):
        for column in range(width):
            if (row, column) in seen:
                continue
            color = int(source[row, column])
            if color == background:
                continue
            stack = [(row, column)]
            seen.add((row, column))
            cells = []
            while stack:
                current = stack.pop()
                cells.append(current)
                for delta_row, delta_column in (
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1),
                ):
                    neighbor = (
                        current[0] + delta_row,
                        current[1] + delta_column,
                    )
                    if (
                        0 <= neighbor[0] < height
                        and 0 <= neighbor[1] < width
                        and neighbor not in seen
                        and int(source[neighbor]) == color
                    ):
                        seen.add(neighbor)
                        stack.append(neighbor)
            rows = [cell[0] for cell in cells]
            columns = [cell[1] for cell in cells]
            output.append(
                _Component(
                    color=color,
                    cells=tuple(sorted(cells)),
                    box=(
                        min(rows),
                        min(columns),
                        max(rows),
                        max(columns),
                    ),
                )
            )
            if len(output) > limits.maximum_components:
                raise RegularSquareCornerMarkLimitError(
                    "component count exceeds representation limit"
                )
    if not output:
        raise RegularSquareCornerMarkAbstention(
            "scene has no foreground components"
        )
    return tuple(output)


def _regular_squares(
    components: Sequence[_Component],
    limits: RegularSquareCornerMarkLimits,
) -> Tuple[_RegularSquare, ...]:
    output = []
    for component in components:
        top, left, bottom, right = component.box
        height = bottom - top + 1
        width = right - left + 1
        if height != width or height < 2:
            continue
        cells = set(component.cells)
        filled = {
            (row, column)
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        }
        perimeter = {
            (row, column)
            for row, column in filled
            if row in {top, bottom} or column in {left, right}
        }
        if cells == filled:
            kind = "filled"
        elif cells == perimeter:
            kind = "one_cell_perimeter"
        else:
            continue
        output.append(
            _RegularSquare(
                kind=kind,
                side=height,
                box=component.box,
            )
        )
        if len(output) > limits.maximum_squares:
            raise RegularSquareCornerMarkLimitError(
                "regular-square count exceeds representation limit"
            )
    if not output:
        raise RegularSquareCornerMarkAbstention(
            "scene has no filled or one-cell-perimeter square"
        )
    return tuple(output)


def _marker_cells(
    source: Array,
    background: int,
    squares: Sequence[_RegularSquare],
    limits: RegularSquareCornerMarkLimits,
) -> Tuple[Cell, ...]:
    height, width = source.shape
    requested: set[Cell] = set()
    for square in squares:
        top, left, bottom, right = square.box
        if top == 0 or left == 0 or bottom == height - 1 or right == width - 1:
            raise RegularSquareCornerMarkAbstention(
                "regular square lacks a complete one-cell exterior workspace"
            )
        local = (
            (top - 1, left),
            (top - 1, right),
            (bottom + 1, left),
            (bottom + 1, right),
            (top, left - 1),
            (bottom, left - 1),
            (top, right + 1),
            (bottom, right + 1),
        )
        if any(int(source[cell]) != background for cell in local):
            raise RegularSquareCornerMarkAbstention(
                "outward corner marker collides with a nonbackground cell"
            )
        if requested.intersection(local):
            raise RegularSquareCornerMarkAbstention(
                "regular squares have overlapping corner-marker roles"
            )
        requested.update(local)
        if len(requested) > limits.maximum_marker_cells:
            raise RegularSquareCornerMarkLimitError(
                "corner-marker count exceeds representation limit"
            )
    return tuple(sorted(requested))


def _execute_with_trace(
    program: RegularSquareCornerMarkProgram,
    grid: Array,
    limits: RegularSquareCornerMarkLimits,
) -> Tuple[Array, RegularSquareCornerMarkTrace]:
    source = _validated_grid(grid, limits)
    background = _background(source)
    if program.paint_color == background:
        raise RegularSquareCornerMarkAbstention(
            "paint color cannot equal the bound background"
        )
    if bool(np.any(source == program.paint_color)):
        raise RegularSquareCornerMarkAbstention(
            "paint color must be novel in every source"
        )
    components = _components(source, background, limits)
    squares = _regular_squares(components, limits)
    markers = _marker_cells(source, background, squares, limits)
    output = source.copy()
    for marker in markers:
        output[marker] = int(program.paint_color)
    if np.array_equal(output, source):
        raise RegularSquareCornerMarkAbstention(
            "regular-square program produced no change"
        )
    trace = RegularSquareCornerMarkTrace(
        background_color=background,
        component_count=len(components),
        square_count=len(squares),
        filled_square_count=sum(
            square.kind == "filled" for square in squares
        ),
        framed_square_count=sum(
            square.kind == "one_cell_perimeter" for square in squares
        ),
        distractor_component_count=len(components) - len(squares),
        square_sides=tuple(sorted(square.side for square in squares)),
        marker_cell_count=len(markers),
    )
    return _validated_grid(output, limits), trace


def execute_regular_square_corner_mark_program(
    program: RegularSquareCornerMarkProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: RegularSquareCornerMarkLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind structural square and corner roles and execute atomically."""

    if not isinstance(program, RegularSquareCornerMarkProgram):
        program = RegularSquareCornerMarkProgram.from_record(program)
    output, _ = _execute_with_trace(program, grid, limits)
    return output.copy()


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _paint_witness(
    source: Array,
    target: Array,
    limits: RegularSquareCornerMarkLimits,
) -> Optional[
    Tuple[
        RegularSquareCornerMarkProgram,
        Array,
        RegularSquareCornerMarkTrace,
        PaintColorWitness,
    ]
]:
    if source.shape != target.shape:
        return None
    try:
        background = _background(source)
    except RegularSquareCornerMarkAbstention:
        return None
    changed = np.argwhere(source != target)
    if len(changed) == 0:
        return None
    if any(int(source[row, column]) != background for row, column in changed):
        return None
    changed_colors = {
        int(target[row, column]) for row, column in changed
    }
    if len(changed_colors) != 1:
        return None
    paint_color = next(iter(changed_colors))
    if paint_color == background or bool(np.any(source == paint_color)):
        return None
    program = RegularSquareCornerMarkProgram(paint_color=paint_color)
    try:
        prediction, trace = _execute_with_trace(program, source, limits)
    except RegularSquareCornerMarkAbstention:
        return None
    if not np.array_equal(prediction, target):
        return None
    witness = PaintColorWitness(
        paint_color=paint_color,
        background_color=background,
        changed_cell_count=len(changed),
        source_palette_size=len(np.unique(source)),
        target_palette_size=len(np.unique(target)),
    )
    return program, prediction, trace, witness


def _infer_exact_program(
    train: Sequence[Tuple[Array, Array]],
    limits: RegularSquareCornerMarkLimits,
) -> Optional[
    Tuple[
        RegularSquareCornerMarkProgram,
        Tuple[Array, ...],
        Tuple[RegularSquareCornerMarkTrace, ...],
        Tuple[PaintColorWitness, ...],
    ]
]:
    if not train:
        return None
    programs = []
    predictions = []
    traces = []
    witnesses = []
    for source, target in train:
        result = _paint_witness(source, target, limits)
        if result is None:
            return None
        program, prediction, trace, witness = result
        programs.append(program)
        predictions.append(prediction)
        traces.append(trace)
        witnesses.append(witness)
    hashes = {program.program_hash() for program in programs}
    if len(hashes) != 1:
        return None
    return (
        programs[0],
        tuple(predictions),
        tuple(traces),
        tuple(witnesses),
    )


def compile_regular_square_corner_mark_program(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: RegularSquareCornerMarkLimits = DEFAULT_LIMITS,
) -> Tuple[RegularSquareCornerMarkCandidate, ...]:
    """Compile the fixed typed schema after exact replay and full LOO."""

    if len(train) < 2:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise RegularSquareCornerMarkLimitError("example budget exceeded")
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
    except RegularSquareCornerMarkAbstention:
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 2:
        return ()

    full = _infer_exact_program(validated, limits)
    if full is None:
        return ()
    program, train_predictions, traces, witnesses = full
    program_hash = program.program_hash()

    loo_program_hashes = []
    loo_exact_count = 0
    for held_index, (held_source, held_target) in enumerate(validated):
        construction = tuple(
            pair
            for index, pair in enumerate(validated)
            if index != held_index
        )
        fold = _infer_exact_program(construction, limits)
        if fold is None or fold[0].program_hash() != program_hash:
            break
        loo_program_hashes.append(fold[0].program_hash())
        try:
            held_prediction = fold[0].apply(held_source, limits=limits)
        except RegularSquareCornerMarkAbstention:
            break
        if not np.array_equal(held_prediction, held_target):
            break
        loo_exact_count += 1
    if loo_exact_count != len(validated):
        return ()

    group_loo_program_hashes = []
    group_loo_exact_count = 0
    for held_indices in groups.values():
        excluded = set(held_indices)
        construction = tuple(
            pair
            for index, pair in enumerate(validated)
            if index not in excluded
        )
        fold = _infer_exact_program(construction, limits)
        if fold is None or fold[0].program_hash() != program_hash:
            break
        group_loo_program_hashes.append(fold[0].program_hash())
        try:
            exact_group = all(
                np.array_equal(
                    fold[0].apply(validated[index][0], limits=limits),
                    validated[index][1],
                )
                for index in held_indices
            )
        except RegularSquareCornerMarkAbstention:
            break
        if not exact_group:
            break
        group_loo_exact_count += 1
    if group_loo_exact_count != len(groups):
        return ()

    try:
        test_predictions = tuple(
            program.apply(test, limits=limits) for test in validated_tests
        )
    except RegularSquareCornerMarkAbstention:
        return ()

    witness_records = [witness.to_record() for witness in witnesses]
    trace_records = [trace.to_record() for trace in traces]
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.regular-square-corner-mark-candidate.v1",
        "program": program.to_record(),
        "program_hash": program_hash,
        "semantic_key": program.semantic_key,
        "operator": OPERATOR,
        "domain": "monochrome_components_4",
        "selector": (
            "ALL_FILLED_OR_ONE_CELL_PERIMETER_SQUARES_SIDE_GE_2"
        ),
        "corner_roles": "FOUR_BOUNDING_BOX_CORNERS",
        "effect": "PAINT_TWO_OUTWARD_CARDINAL_NEIGHBORS_PER_CORNER",
        "collision_policy": "require_complete_disjoint_background_workspace",
        "background_binding": "unique_global_mode",
        "paint_color_binding": "unanimous_novel_added_color",
        "paint_color_witness": {
            "resolved_paint_color": int(program.paint_color),
            "per_example": witness_records,
            "unanimous": True,
            "background_only_changes": True,
            "source_absent_in_every_example": True,
        },
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "raw_grid_free_program": True,
        "literal_coordinate_free_program": True,
        "component_color_free_selector": True,
        "component_size_free_program": True,
        "paint_color_is_demonstration_inferred": True,
        "palette_equivariant": False,
        "d4_equivariant": True,
        "quarter_turn_equivariant": True,
        "witness_protocol": "full_demonstration_and_distinct_group_loo_reinduction",
        "distinct_witness_groups": int(len(groups)),
        "loo_exact_count": int(loo_exact_count),
        "loo_total_count": int(len(validated)),
        "loo_program_hashes": list(loo_program_hashes),
        "distinct_group_loo_exact_count": int(group_loo_exact_count),
        "distinct_group_loo_total_count": int(len(groups)),
        "distinct_group_loo_program_hashes": list(
            group_loo_program_hashes
        ),
        "witness_reconstructible": True,
        "training_trace_summary": trace_records,
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": (
            regular_square_corner_mark_implementation_fingerprint()
        ),
        "limits": limits.to_record(),
    }
    return (
        RegularSquareCornerMarkCandidate(
            name=(
                "regular_square_corner_mark:outward_corner_neighbors:"
                f"{program_hash[:12]}"
            ),
            program=program,
            grids=test_predictions,
            train_grids=train_predictions,
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


regular_square_corner_mark_candidates = (
    compile_regular_square_corner_mark_program
)


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "OPERATOR",
    "PaintColorWitness",
    "RegularSquareCornerMarkAbstention",
    "RegularSquareCornerMarkCandidate",
    "RegularSquareCornerMarkError",
    "RegularSquareCornerMarkLimitError",
    "RegularSquareCornerMarkLimits",
    "RegularSquareCornerMarkProgram",
    "RegularSquareCornerMarkTrace",
    "compile_regular_square_corner_mark_program",
    "execute_regular_square_corner_mark_program",
    "regular_square_corner_mark_candidates",
    "regular_square_corner_mark_implementation_fingerprint",
]
