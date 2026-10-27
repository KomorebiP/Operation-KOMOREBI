"""Exact normalization of axis-aligned lines crossing a rectangular frame.

The executor recognizes one complete monochrome rectangular frame and one or
two axis-aligned payload lines.  A payload line occupies an entire strict-
interior row or column and has contiguous, nonempty extensions on both sides
of the frame.  Frame cells occlude the payload at the perimeter.

The bounded compiler learns an explicit orientation-to-side relation from the
demonstrations.  A horizontal line may be normalized to the top or bottom
frame side; a vertical line may be normalized to the left or right side.  The
interior segment and the old exterior extensions are erased, then the exterior
payload packets are placed beside the selected side.  The frame and every
unrelated cell are preserved.

Geometry is input-only.  Outputs only select among four finite side mappings,
and a mapping must reproduce every demonstration exactly.  All rendering uses
an immutable source, collisions cause abstention, and exact-demo mappings that
disagree on held-out grids are not guessed between.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
from typing import Dict, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    from .closed_container_rewrite import (
        ClosedContainer,
        ClosedContainerAmbiguityError,
        ClosedContainerError,
        ClosedContainerLimits,
        detect_closed_rectangular_containers,
    )
    from .planar_incidence import AmbiguousBackgroundError, infer_background
except ImportError:  # standalone Kaggle runtime
    from closed_container_rewrite import (
        ClosedContainer,
        ClosedContainerAmbiguityError,
        ClosedContainerError,
        ClosedContainerLimits,
        detect_closed_rectangular_containers,
    )
    from planar_incidence import AmbiguousBackgroundError, infer_background


Array = np.ndarray
Cell = Tuple[int, int]

CROSSING_LINE_NORMALIZATION_VERSION = "1.0"


class CrossingLineError(ValueError):
    """Base class for explicit crossing-line abstentions."""


class CrossingLineAmbiguityError(CrossingLineError):
    """Raised when an orientation has zero or multiple structural readings."""


class CrossingLineConflictError(CrossingLineError):
    """Raised when an atomic normalization would overwrite unrelated cells."""


class CrossingLineLimitError(CrossingLineError):
    """Raised before a configured input or hypothesis budget is exceeded."""


@dataclass(frozen=True)
class CrossingLineLimits:
    maximum_height: int = 30
    maximum_width: int = 30
    maximum_line_candidates: int = 8
    maximum_programs: int = 4
    container_limits: ClosedContainerLimits = ClosedContainerLimits()


DEFAULT_LIMITS = CrossingLineLimits()


@dataclass(frozen=True)
class CrossingLine:
    """One input-grounded payload line interrupted by a frame perimeter."""

    orientation: str
    color: int
    axis: int
    interior_cells: Tuple[Cell, ...]
    negative_extension: Tuple[Cell, ...]
    positive_extension: Tuple[Cell, ...]

    def __post_init__(self) -> None:
        if self.orientation not in {"horizontal", "vertical"}:
            raise CrossingLineError(f"unknown orientation {self.orientation!r}")
        if not self.interior_cells:
            raise CrossingLineError("crossing line has no strict-interior segment")
        if not self.negative_extension or not self.positive_extension:
            raise CrossingLineError("crossing line must extend beyond both frame sides")

    @property
    def source_cells(self) -> Tuple[Cell, ...]:
        return tuple(
            sorted(
                set(self.interior_cells)
                | set(self.negative_extension)
                | set(self.positive_extension)
            )
        )

    @property
    def exterior_cells(self) -> Tuple[Cell, ...]:
        return tuple(
            sorted(set(self.negative_extension) | set(self.positive_extension))
        )

    def json_record(self) -> Dict[str, object]:
        """Return structural evidence without retaining raster coordinates."""

        return {
            "orientation": self.orientation,
            "payload_color": int(self.color),
            "interior_length": len(self.interior_cells),
            "negative_extension_length": len(self.negative_extension),
            "positive_extension_length": len(self.positive_extension),
        }


_VALID_SIDES = {
    "horizontal": ("top", "bottom"),
    "vertical": ("left", "right"),
}


@dataclass(frozen=True)
class CrossingLineProgram:
    """A witnessed mapping from payload orientation to a parallel frame side."""

    orientation_sides: Tuple[Tuple[str, str], ...]
    quantifier: str = "FOR_EACH"

    def __post_init__(self) -> None:
        if self.quantifier != "FOR_EACH":
            raise CrossingLineError("the crossing-line compiler supports only FOR_EACH")
        mapping = dict(self.orientation_sides)
        if len(mapping) != len(self.orientation_sides) or not mapping:
            raise CrossingLineError("orientation mapping is empty or duplicated")
        if tuple(sorted(mapping)) != tuple(key for key, _ in self.orientation_sides):
            raise CrossingLineError("orientation mapping must use canonical order")
        for orientation, side in mapping.items():
            if side not in _VALID_SIDES.get(orientation, ()):
                raise CrossingLineError(
                    f"side {side!r} is not parallel to {orientation!r} payloads"
                )

    @property
    def side_by_orientation(self) -> Dict[str, str]:
        return dict(self.orientation_sides)

    @property
    def complexity(self) -> int:
        return 8 + len(self.orientation_sides)

    @property
    def semantic_key(self) -> str:
        mapping = ",".join(f"{orientation}->{side}" for orientation, side in self.orientation_sides)
        return f"crossing_line|FOR_EACH|{mapping}|preserve_frame"

    def json_record(self) -> Dict[str, object]:
        return {
            "quantifier": self.quantifier,
            "orientation_side_mapping": {
                orientation: side for orientation, side in self.orientation_sides
            },
            "semantic_key": self.semantic_key,
        }


@dataclass(frozen=True)
class CrossingLineTrace:
    line_count: int
    removed_interior_cells: int
    relocated_exterior_cells: int
    cleared_old_exterior_cells: int
    requested_write_cells: int

    def json_record(self) -> Dict[str, int]:
        return {
            "line_count": int(self.line_count),
            "removed_interior_cells": int(self.removed_interior_cells),
            "relocated_exterior_cells": int(self.relocated_exterior_cells),
            "cleared_old_exterior_cells": int(self.cleared_old_exterior_cells),
            "requested_write_cells": int(self.requested_write_cells),
        }


@dataclass(frozen=True)
class CrossingLineCandidate:
    name: str
    family: str
    complexity: int
    train_error: int
    program: CrossingLineProgram
    train_grids: Tuple[Array, ...]
    grids: Tuple[Array, ...]
    metadata: Mapping[str, object]

    def json_record(self) -> Dict[str, object]:
        return {
            "name": str(self.name),
            "family": str(self.family),
            "complexity": int(self.complexity),
            "train_error": int(self.train_error),
            "program": self.program.json_record(),
            "train_grids": [_grid_list(grid) for grid in self.train_grids],
            "grids": [_grid_list(grid) for grid in self.grids],
            "metadata": _json_safe(self.metadata),
        }


def _grid(grid: Array) -> Array:
    value = np.asarray(grid, dtype=np.int16)
    if value.ndim != 2 or value.size == 0:
        raise CrossingLineError("crossing-line analysis requires a nonempty 2D grid")
    return np.ascontiguousarray(value)


def _grid_list(grid: Array) -> list[list[int]]:
    return [[int(value) for value in row] for row in _grid(grid).tolist()]


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    raise TypeError(f"value of type {type(value).__name__} is not JSON-safe")


def _contiguous_extension(
    source: Array,
    *,
    start: Cell,
    step: Cell,
    color: int,
) -> Tuple[Cell, ...]:
    height, width = source.shape
    row, column = start
    dr, dc = step
    cells = []
    while 0 <= row < height and 0 <= column < width and int(source[row, column]) == color:
        cells.append((row, column))
        row += dr
        column += dc
    return tuple(cells)


def _horizontal_candidates(
    source: Array,
    frame: ClosedContainer,
    background: int,
) -> Tuple[CrossingLine, ...]:
    output = []
    for row in range(frame.top + 1, frame.bottom):
        interior = source[row, frame.left + 1 : frame.right]
        if interior.size == 0 or not bool(np.all(interior == interior[0])):
            continue
        color = int(interior[0])
        if color in {background, int(frame.color)}:
            continue
        negative = _contiguous_extension(
            source,
            start=(row, frame.left - 1),
            step=(0, -1),
            color=color,
        ) if frame.left > 0 else ()
        positive = _contiguous_extension(
            source,
            start=(row, frame.right + 1),
            step=(0, 1),
            color=color,
        ) if frame.right + 1 < source.shape[1] else ()
        if not negative or not positive:
            continue
        output.append(
            CrossingLine(
                orientation="horizontal",
                color=color,
                axis=row,
                interior_cells=tuple(
                    (row, column)
                    for column in range(frame.left + 1, frame.right)
                ),
                negative_extension=tuple(sorted(negative)),
                positive_extension=tuple(sorted(positive)),
            )
        )
    return tuple(output)


def _vertical_candidates(
    source: Array,
    frame: ClosedContainer,
    background: int,
) -> Tuple[CrossingLine, ...]:
    output = []
    for column in range(frame.left + 1, frame.right):
        interior = source[frame.top + 1 : frame.bottom, column]
        if interior.size == 0 or not bool(np.all(interior == interior[0])):
            continue
        color = int(interior[0])
        if color in {background, int(frame.color)}:
            continue
        negative = _contiguous_extension(
            source,
            start=(frame.top - 1, column),
            step=(-1, 0),
            color=color,
        ) if frame.top > 0 else ()
        positive = _contiguous_extension(
            source,
            start=(frame.bottom + 1, column),
            step=(1, 0),
            color=color,
        ) if frame.bottom + 1 < source.shape[0] else ()
        if not negative or not positive:
            continue
        output.append(
            CrossingLine(
                orientation="vertical",
                color=color,
                axis=column,
                interior_cells=tuple(
                    (row, column)
                    for row in range(frame.top + 1, frame.bottom)
                ),
                negative_extension=tuple(sorted(negative)),
                positive_extension=tuple(sorted(positive)),
            )
        )
    return tuple(output)


def detect_frame_crossing_lines(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: CrossingLineLimits = DEFAULT_LIMITS,
) -> Tuple[ClosedContainer, Tuple[CrossingLine, ...]]:
    """Return a unique frame and at most one crossing line per orientation."""

    source = _grid(grid)
    if source.shape[0] > limits.maximum_height or source.shape[1] > limits.maximum_width:
        raise CrossingLineLimitError("grid exceeds the crossing-line shape bound")
    try:
        resolved_background = infer_background(source) if background is None else int(background)
    except AmbiguousBackgroundError as error:
        raise CrossingLineAmbiguityError(str(error)) from error
    try:
        frames = detect_closed_rectangular_containers(
            source,
            background=resolved_background,
            limits=limits.container_limits,
        )
    except ClosedContainerAmbiguityError as error:
        raise CrossingLineAmbiguityError(str(error)) from error
    except ClosedContainerError as error:
        raise CrossingLineError(str(error)) from error
    if len(frames) != 1:
        raise CrossingLineAmbiguityError("crossing-line normalization requires one unique frame")
    frame = frames[0]
    candidates = _horizontal_candidates(source, frame, resolved_background) + _vertical_candidates(
        source,
        frame,
        resolved_background,
    )
    if len(candidates) > limits.maximum_line_candidates:
        raise CrossingLineLimitError("crossing-line candidate budget exceeded")
    by_orientation: Dict[str, list[CrossingLine]] = {}
    for line in candidates:
        by_orientation.setdefault(line.orientation, []).append(line)
    if not by_orientation:
        raise CrossingLineError("no axis-aligned payload crosses the frame")
    tied = [orientation for orientation, values in by_orientation.items() if len(values) != 1]
    if tied:
        raise CrossingLineAmbiguityError(
            "crossing-line orientation tie: " + ",".join(sorted(tied))
        )
    lines = tuple(by_orientation[key][0] for key in sorted(by_orientation))
    return frame, lines


def _target_cell(
    cell: Cell,
    line: CrossingLine,
    frame: ClosedContainer,
    side: str,
) -> Cell:
    row, column = cell
    if line.orientation == "horizontal":
        return (frame.top if side == "top" else frame.bottom, column)
    return (row, frame.left if side == "left" else frame.right)


def apply_crossing_line_program(
    grid: Array,
    program: CrossingLineProgram,
    *,
    representation: Optional[Tuple[ClosedContainer, Sequence[CrossingLine]]] = None,
    background: Optional[int] = None,
    limits: CrossingLineLimits = DEFAULT_LIMITS,
) -> Tuple[Array, CrossingLineTrace]:
    """Apply a side-normalization program atomically to one immutable source."""

    source = _grid(grid)
    try:
        resolved_background = infer_background(source) if background is None else int(background)
    except AmbiguousBackgroundError as error:
        raise CrossingLineAmbiguityError(str(error)) from error
    if representation is None:
        frame, raw_lines = detect_frame_crossing_lines(
            source,
            background=resolved_background,
            limits=limits,
        )
        lines = tuple(raw_lines)
    else:
        frame, raw_lines = representation
        lines = tuple(raw_lines)
    if not lines:
        raise CrossingLineError("normalization selected no crossing payload")
    mapping = program.side_by_orientation
    if any(line.orientation not in mapping for line in lines):
        raise CrossingLineError("program lacks a witnessed side for an orientation")

    selected_source_cells = {cell for line in lines for cell in line.source_cells}
    assignments: Dict[Cell, int] = {}

    def assign(cell: Cell, value: int) -> None:
        previous = assignments.get(cell)
        if previous is not None and int(previous) != int(value):
            raise CrossingLineConflictError(f"conflicting writes at {cell!r}")
        assignments[cell] = int(value)

    for cell in sorted(selected_source_cells):
        assign(cell, resolved_background)

    relocated = 0
    for line in lines:
        side = mapping[line.orientation]
        for source_cell in line.exterior_cells:
            target_cell = _target_cell(source_cell, line, frame, side)
            target_source_value = int(source[target_cell])
            if (
                target_cell not in selected_source_cells
                and target_source_value not in {resolved_background, int(line.color)}
            ):
                raise CrossingLineConflictError(
                    "relocated exterior would overwrite an unrelated cell"
                )
            assign(target_cell, int(line.color))
            relocated += 1

    output = source.copy()
    for cell, value in sorted(assignments.items()):
        output[cell] = int(value)
    if np.array_equal(output, source):
        raise CrossingLineError("crossing-line normalization is vacuous")
    trace = CrossingLineTrace(
        line_count=len(lines),
        removed_interior_cells=len({cell for line in lines for cell in line.interior_cells}),
        relocated_exterior_cells=relocated,
        cleared_old_exterior_cells=len(
            {cell for line in lines for cell in line.exterior_cells}
        ),
        requested_write_cells=len(assignments),
    )
    return output, trace


def _prediction_digest(grids: Sequence[Array]) -> str:
    digest = hashlib.sha256()
    for grid in grids:
        value = _grid(grid)
        digest.update(int(value.shape[0]).to_bytes(2, "little"))
        digest.update(int(value.shape[1]).to_bytes(2, "little"))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _programs(orientations: Sequence[str]) -> Tuple[CrossingLineProgram, ...]:
    ordered = tuple(sorted(set(orientations)))
    if not ordered:
        return ()
    output = []
    for sides in itertools.product(*(_VALID_SIDES[orientation] for orientation in ordered)):
        output.append(CrossingLineProgram(tuple(zip(ordered, sides))))
    return tuple(output)


def _aggregate_traces(traces: Sequence[CrossingLineTrace]) -> Dict[str, int]:
    records = [trace.json_record() for trace in traces]
    return {
        "demonstrations": len(records),
        "selected_lines": sum(record["line_count"] for record in records),
        "multi_line_demonstrations": sum(record["line_count"] >= 2 for record in records),
        "removed_interior_cells": sum(record["removed_interior_cells"] for record in records),
        "relocated_exterior_cells": sum(record["relocated_exterior_cells"] for record in records),
        "cleared_old_exterior_cells": sum(record["cleared_old_exterior_cells"] for record in records),
        "requested_write_cells": sum(record["requested_write_cells"] for record in records),
    }


def compile_crossing_line_normalizations(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: CrossingLineLimits = DEFAULT_LIMITS,
) -> Tuple[CrossingLineCandidate, ...]:
    """Compile one exact orientation-to-side normalization, or abstain."""

    if not train or not tests:
        return ()
    try:
        normalized_train = tuple((_grid(source), _grid(target)) for source, target in train)
        normalized_tests = tuple(_grid(source) for source in tests)
        if not all(source.shape == target.shape for source, target in normalized_train):
            return ()
        train_representations = tuple(
            detect_frame_crossing_lines(source, limits=limits)
            for source, _ in normalized_train
        )
        test_representations = tuple(
            detect_frame_crossing_lines(source, limits=limits)
            for source in normalized_tests
        )
    except CrossingLineError:
        return ()
    witnessed_orientations = tuple(
        sorted(
            {
                line.orientation
                for _, lines in train_representations
                for line in lines
            }
        )
    )
    test_orientations = {
        line.orientation for _, lines in test_representations for line in lines
    }
    if not test_orientations.issubset(set(witnessed_orientations)):
        return ()
    programs = _programs(witnessed_orientations)
    if len(programs) > limits.maximum_programs:
        return ()

    exact_programs = []
    for program in programs:
        try:
            train_results = tuple(
                apply_crossing_line_program(
                    source,
                    program,
                    representation=representation,
                    limits=limits,
                )
                for (source, _), representation in zip(
                    normalized_train,
                    train_representations,
                )
            )
            train_predictions = tuple(result[0] for result in train_results)
            if not all(
                np.array_equal(prediction, target)
                for prediction, (_, target) in zip(train_predictions, normalized_train)
            ):
                continue
            test_results = tuple(
                apply_crossing_line_program(
                    source,
                    program,
                    representation=representation,
                    limits=limits,
                )
                for source, representation in zip(normalized_tests, test_representations)
            )
        except CrossingLineError:
            continue
        exact_programs.append(
            (
                program,
                train_predictions,
                tuple(result[0] for result in test_results),
                tuple(result[1] for result in train_results),
            )
        )
    if not exact_programs:
        return ()
    groups: Dict[str, list[object]] = {}
    for record in exact_programs:
        groups.setdefault(_prediction_digest(record[2]), []).append(record)
    if len(groups) != 1:
        return ()
    aliases = next(iter(groups.values()))
    chosen = min(aliases, key=lambda item: (item[0].complexity, item[0].semantic_key))
    program, train_predictions, test_predictions, train_traces = chosen
    evidence = _aggregate_traces(train_traces)
    train_line_counts = [len(lines) for _, lines in train_representations]
    test_line_counts = [len(lines) for _, lines in test_representations]
    metadata: Dict[str, object] = {
        "compiler_block": "crossing_line_normalization",
        "compiler_version": CROSSING_LINE_NORMALIZATION_VERSION,
        "typed_entities": [
            "unique_complete_monochrome_rectangular_perimeter",
            "axis_aligned_bilateral_crossing_payload",
        ],
        "representation_source": "input_only",
        "background_policy": "input_only_structural_inference",
        "selector": "unique_crossing_line_per_orientation",
        "quantifier": "FOR_EACH",
        "orientation_side_mapping": program.side_by_orientation,
        "renderer": "atomic_relocate_exterior_and_erase_interior_crossing",
        "frame_policy": "preserve_exactly",
        "unrelated_cell_policy": "preserve_exactly",
        "effect_conditioned": True,
        "effect_evidence": evidence,
        "semantic_mechanism_key": program.semantic_key,
        "semantic_alias_count": len(aliases),
        "semantic_aliases": sorted(item[0].semantic_key for item in aliases),
        "version_space_ties_diverging_on_tests": 0,
        "immutable_source_rendering": True,
        "write_conflict_policy": "abstain",
        "output_shape_contract": "same_as_test_input",
        "output_lineage": {
            "kind": "test_input_frame_crossing_normalization",
            "geometry": "test_input_detected_frame_and_crossing_lines",
            "payload_color": "source_line_color",
        },
        "provenance_kind": "test_input_structural_role_transform",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "d4_relation_consistent": True,
        "task_palette_equivariant": True,
        "admissible": True,
        "partial_program": True,
        "stores_coordinates": False,
        "stores_training_rasters": False,
        "stores_task_ids": False,
        "exact_demonstration_contract": True,
        "train_line_count_min": min(train_line_counts),
        "train_line_count_max": max(train_line_counts),
        "test_line_count_min": min(test_line_counts),
        "test_line_count_max": max(test_line_counts),
        "resource_limits": {
            "maximum_height": int(limits.maximum_height),
            "maximum_width": int(limits.maximum_width),
            "maximum_line_candidates": int(limits.maximum_line_candidates),
            "maximum_programs": int(limits.maximum_programs),
        },
    }
    return (
        CrossingLineCandidate(
            name=f"crossing_line_{program.semantic_key}",
            family="causal_crossing_line_normalization",
            complexity=program.complexity,
            train_error=0,
            program=program,
            train_grids=tuple(grid.copy() for grid in train_predictions),
            grids=tuple(grid.copy() for grid in test_predictions),
            metadata=metadata,
        ),
    )


__all__ = [
    "CROSSING_LINE_NORMALIZATION_VERSION",
    "CrossingLine",
    "CrossingLineAmbiguityError",
    "CrossingLineCandidate",
    "CrossingLineConflictError",
    "CrossingLineError",
    "CrossingLineLimitError",
    "CrossingLineLimits",
    "CrossingLineProgram",
    "CrossingLineTrace",
    "DEFAULT_LIMITS",
    "apply_crossing_line_program",
    "compile_crossing_line_normalizations",
    "detect_frame_crossing_lines",
]
