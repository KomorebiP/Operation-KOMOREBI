"""Bounded compiler for minor-canvas barrier faces.

This module is intentionally separate from the solver portfolio. It compiles
one fixed, input-grounded relational program:

1. infer a unique top-ranked background;
2. choose the unique largest non-background color as a barrier role;
3. construct per-color barrier faces;
4. select every face that occupies less than half of every canvas side; and
5. recolor only background cells in those faces with the barrier color.

The half-side test is scale-normalized and D4 equivariant. Strictly enclosed
faces have zero canvas exposure and therefore satisfy it automatically. Faces
closed partly by the virtual canvas also qualify when their exposure remains
minor. Demonstrations are used only for exact program verification. No task
identifier, coordinate, held-out output, or fitted numeric threshold enters
the program.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence, Tuple

import numpy as np

try:
    from .barrier_faces import (
        BarrierFace,
        BarrierFaceError,
        BarrierFaceHypothesis,
        BarrierFaceLimitError,
        BarrierFaceLimits,
        BarrierPolicy,
        DEFAULT_LIMITS,
        build_barrier_face_hypothesis,
    )
    from .planar_incidence import rank_background_hypotheses
except ImportError:  # standalone Kaggle runtime
    from barrier_faces import (
        BarrierFace,
        BarrierFaceError,
        BarrierFaceHypothesis,
        BarrierFaceLimitError,
        BarrierFaceLimits,
        BarrierPolicy,
        DEFAULT_LIMITS,
        build_barrier_face_hypothesis,
    )
    from planar_incidence import rank_background_hypotheses


Array = np.ndarray
TrainPair = Tuple[Array, Array]

BARRIER_FACE_COMPILER_VERSION = "1.1"
MAXIMUM_COMPILER_EXAMPLES = 16
MAXIMUM_COMPILER_CELLS = 21600


class BarrierFaceCompilerError(ValueError):
    """Base class for explicit compiler abstentions."""


class BarrierFaceCompilerAmbiguity(BarrierFaceCompilerError):
    """Raised when an input-derived role is not unique."""


@dataclass(frozen=True)
class BarrierFaceProgram:
    background_role: str = "unique_top_ranked_background"
    barrier_role: str = "unique_largest_nonbackground_area"
    quantifier: str = "FOR_EACH"
    face_selector: str = "no_majority_canvas_side"
    renderer: str = "fill_background_cells_with_barrier_color"

    def __post_init__(self) -> None:
        expected = (
            self.background_role == "unique_top_ranked_background"
            and self.barrier_role == "unique_largest_nonbackground_area"
            and self.quantifier == "FOR_EACH"
            and self.face_selector == "no_majority_canvas_side"
            and self.renderer == "fill_background_cells_with_barrier_color"
        )
        if not expected:
            raise BarrierFaceCompilerError("unsupported barrier-face program")

    @property
    def complexity(self) -> int:
        return 11

    @property
    def semantic_key(self) -> str:
        return (
            "barrier_face|unique_largest_foreground|FOR_EACH|"
            "no_majority_canvas_side|background_to_barrier"
        )

    def json_record(self) -> Dict[str, object]:
        return {
            "background_role": self.background_role,
            "barrier_role": self.barrier_role,
            "quantifier": self.quantifier,
            "face_selector": self.face_selector,
            "renderer": self.renderer,
            "semantic_key": self.semantic_key,
            "scale_normalized_threshold": "strictly_less_than_one_half_per_side",
        }


DEFAULT_PROGRAM = BarrierFaceProgram()


@dataclass(frozen=True)
class BarrierFaceApplicationTrace:
    face_count: int
    selected_face_count: int
    enclosed_selected_faces: int
    virtual_canvas_selected_faces: int
    changed_background_cells: int
    preserved_occupant_cells: int
    absorbed_wall_cells: int
    hypothesis_digest: str

    def json_record(self) -> Dict[str, object]:
        return {
            "face_count": int(self.face_count),
            "selected_face_count": int(self.selected_face_count),
            "enclosed_selected_faces": int(self.enclosed_selected_faces),
            "virtual_canvas_selected_faces": int(self.virtual_canvas_selected_faces),
            "changed_background_cells": int(self.changed_background_cells),
            "preserved_occupant_cells": int(self.preserved_occupant_cells),
            "absorbed_wall_cells": int(self.absorbed_wall_cells),
            "hypothesis_digest": str(self.hypothesis_digest),
        }


@dataclass(frozen=True)
class BarrierFaceRewriteCandidate:
    name: str
    family: str
    complexity: int
    train_error: int
    program: BarrierFaceProgram
    train_grids: Tuple[Array, ...]
    grids: Tuple[Array, ...]
    metadata: Mapping[str, object]

    def json_record(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "family": self.family,
            "complexity": int(self.complexity),
            "train_error": int(self.train_error),
            "program": self.program.json_record(),
            "train_grids": [_grid_list(grid) for grid in self.train_grids],
            "grids": [_grid_list(grid) for grid in self.grids],
            "metadata": _json_safe(self.metadata),
        }


def _grid(
    grid: Array,
    limits: BarrierFaceLimits = DEFAULT_LIMITS,
) -> Array:
    value = np.asarray(grid)
    if value.ndim != 2 or value.size == 0:
        raise BarrierFaceCompilerError("compiler requires a nonempty 2D grid")
    if not np.issubdtype(value.dtype, np.number):
        raise BarrierFaceCompilerError("grid values must be numeric")
    if not np.all(np.isfinite(value)):
        raise BarrierFaceCompilerError("grid values must be finite")
    if np.issubdtype(value.dtype, np.floating):
        outside_int64 = np.any(value < -float(2**63)) or np.any(value >= float(2**63))
    elif np.issubdtype(value.dtype, np.unsignedinteger):
        outside_int64 = bool(np.any(value > np.iinfo(np.int64).max))
    else:
        outside_int64 = False
    if outside_int64:
        raise BarrierFaceCompilerError("grid values exceed the signed 64-bit range")
    if not np.issubdtype(value.dtype, np.integer):
        if not np.all(np.equal(value, np.floor(value))):
            raise BarrierFaceCompilerError("grid values must be integers")
    height, width = value.shape
    shape_orbit = (min(height, width), max(height, width))
    limit_orbit = (
        min(limits.maximum_height, limits.maximum_width),
        max(limits.maximum_height, limits.maximum_width),
    )
    if shape_orbit[0] > limit_orbit[0] or shape_orbit[1] > limit_orbit[1]:
        raise BarrierFaceLimitError(
            f"grid shape {value.shape} exceeds "
            f"{limits.maximum_height}x{limits.maximum_width}"
        )
    if len(np.unique(value)) > limits.maximum_palette:
        raise BarrierFaceLimitError("palette budget exceeded")
    return np.array(value, dtype=np.int64, copy=True)


def _grid_list(grid: Array) -> list[list[int]]:
    return [[int(value) for value in row] for row in _grid(grid).tolist()]


def _json_safe(value: object) -> object:
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _input_roles(grid: Array) -> Tuple[int, int]:
    value = np.asarray(grid)
    background_hypotheses = rank_background_hypotheses(value)
    leaders = [item for item in background_hypotheses if item.rank == 0]
    if len(leaders) != 1:
        raise BarrierFaceCompilerAmbiguity("background role is not unique")
    background = int(leaders[0].color)
    counts = [
        (int(count), int(color))
        for color, count in zip(*np.unique(value, return_counts=True))
        if int(color) != background
    ]
    if not counts:
        raise BarrierFaceCompilerAmbiguity("barrier role has no foreground colors")
    counts.sort(reverse=True)
    if len(counts) > 1 and counts[0][0] == counts[1][0]:
        raise BarrierFaceCompilerAmbiguity("largest foreground role is tied")
    return background, counts[0][1]


def _barrier_hypothesis(
    grid: Array,
    background: int,
    barrier: int,
    limits: BarrierFaceLimits,
) -> BarrierFaceHypothesis:
    return build_barrier_face_hypothesis(
        grid,
        background=background,
        policy=BarrierPolicy("per_color", barrier),
        limits=limits,
    )


def face_has_majority_canvas_side(face: BarrierFace, shape: Tuple[int, int]) -> bool:
    """Whether ``face`` occupies at least half of any complete canvas side."""

    height, width = shape
    top, right, bottom, left = face.canvas_contacts
    return (
        2 * top >= width
        or 2 * bottom >= width
        or 2 * left >= height
        or 2 * right >= height
    )


def select_minor_canvas_faces(
    hypothesis: BarrierFaceHypothesis,
) -> Tuple[BarrierFace, ...]:
    return tuple(
        face
        for face in hypothesis.faces
        if not face_has_majority_canvas_side(face, hypothesis.shape)
    )


def apply_barrier_face_program(
    grid: Array,
    program: BarrierFaceProgram = DEFAULT_PROGRAM,
    *,
    limits: BarrierFaceLimits = DEFAULT_LIMITS,
) -> Tuple[Array, BarrierFaceApplicationTrace]:
    """Apply the fixed program using input-derived roles only."""

    if type(program) is not BarrierFaceProgram or program != DEFAULT_PROGRAM:
        raise BarrierFaceCompilerError("unsupported barrier-face program")
    source = _grid(grid, limits)
    background, barrier = _input_roles(source)
    hypothesis = _barrier_hypothesis(source, background, barrier, limits)
    selected = select_minor_canvas_faces(hypothesis)
    if not selected:
        raise BarrierFaceCompilerError("minor-canvas selector has no positive face")
    if len(selected) == len(hypothesis.faces):
        raise BarrierFaceCompilerError("minor-canvas selector lacks negative support")

    output = source.copy()
    changed = 0
    preserved_occupants = 0
    for face in selected:
        face_background_cells = 0
        for row, column in face.cells:
            if int(source[row, column]) == background:
                face_background_cells += 1
                if int(output[row, column]) != barrier:
                    output[row, column] = barrier
                    changed += 1
            else:
                preserved_occupants += 1
        if face_background_cells <= 0:
            raise BarrierFaceCompilerError(
                "selected face lacks observable background support"
            )
    if changed <= 0:
        raise BarrierFaceCompilerError("barrier-face renderer is vacuous")
    trace = BarrierFaceApplicationTrace(
        face_count=len(hypothesis.faces),
        selected_face_count=len(selected),
        enclosed_selected_faces=sum(face.strictly_enclosed for face in selected),
        virtual_canvas_selected_faces=sum(face.uses_virtual_canvas for face in selected),
        changed_background_cells=changed,
        preserved_occupant_cells=preserved_occupants,
        absorbed_wall_cells=hypothesis.absorbed_wall_cells,
        hypothesis_digest=hypothesis.normalized_digest(),
    )
    return output, trace


def _exact(first: Array, second: Array) -> bool:
    return np.array_equal(np.asarray(first), np.asarray(second))


def compile_barrier_face_fill_rule(
    train: Sequence[TrainPair],
    tests: Sequence[Array],
    *,
    limits: BarrierFaceLimits = DEFAULT_LIMITS,
) -> Tuple[BarrierFaceRewriteCandidate, ...]:
    """Exact-fit compiler for the fixed minor-canvas face program."""

    if not train or not tests:
        return ()
    if len(train) + len(tests) > MAXIMUM_COMPILER_EXAMPLES:
        return ()
    task_cells = sum(
        int(np.asarray(source).size) + int(np.asarray(target).size)
        for source, target in train
    ) + sum(int(np.asarray(source).size) for source in tests)
    if task_cells > MAXIMUM_COMPILER_CELLS:
        return ()
    program = DEFAULT_PROGRAM
    train_predictions = []
    train_traces = []
    test_predictions = []
    test_traces = []
    try:
        for source_raw, target_raw in train:
            source = _grid(source_raw, limits)
            target = _grid(target_raw, limits)
            if source.shape != target.shape:
                return ()
            prediction, trace = apply_barrier_face_program(
                source, program, limits=limits
            )
            if not _exact(prediction, target):
                return ()
            train_predictions.append(prediction)
            train_traces.append(trace)
        for source_raw in tests:
            prediction, trace = apply_barrier_face_program(
                _grid(source_raw, limits), program, limits=limits
            )
            test_predictions.append(prediction)
            test_traces.append(trace)
    except (BarrierFaceCompilerError, BarrierFaceError, ValueError):
        return ()

    total_selected = sum(trace.selected_face_count for trace in train_traces)
    total_unselected = sum(
        trace.face_count - trace.selected_face_count for trace in train_traces
    )
    if total_selected <= 0 or total_unselected <= 0:
        return ()
    metadata: Dict[str, object] = {
        "compiler_block": "per_color_barrier_face_hypothesis",
        "typed_entity": "barrier_complement_face",
        "program": program.json_record(),
        "stores_coordinates": False,
        "stores_training_rasters": False,
        "candidate_contract_retains_exact_train_predictions": True,
        "input_only_roles": True,
        "d4_equivariant": True,
        "palette_equivariant": True,
        "scale_normalized": True,
        "effect_evidence": {
            "training_examples": len(train),
            "selected_faces": total_selected,
            "unselected_faces": total_unselected,
            "strictly_enclosed_selected_faces": sum(
                trace.enclosed_selected_faces for trace in train_traces
            ),
            "virtual_canvas_selected_faces": sum(
                trace.virtual_canvas_selected_faces for trace in train_traces
            ),
            "changed_background_cells": sum(
                trace.changed_background_cells for trace in train_traces
            ),
            "preserved_occupant_cells": sum(
                trace.preserved_occupant_cells for trace in train_traces
            ),
            "absorbed_wall_cells": sum(
                trace.absorbed_wall_cells for trace in train_traces
            ),
        },
        "output_lineage": {
            "kind": "test_input_face_transform",
            "source_cells": "selected_face_background_cells",
            "target_role": "input_derived_barrier_color",
        },
    }
    return (
        BarrierFaceRewriteCandidate(
            name="fill_minor_canvas_faces_from_unique_largest_barrier",
            family="causal_barrier_face_fill",
            complexity=program.complexity,
            train_error=0,
            program=program,
            train_grids=tuple(train_predictions),
            grids=tuple(test_predictions),
            metadata=metadata,
        ),
    )


__all__ = [
    "BARRIER_FACE_COMPILER_VERSION",
    "MAXIMUM_COMPILER_CELLS",
    "MAXIMUM_COMPILER_EXAMPLES",
    "BarrierFaceApplicationTrace",
    "BarrierFaceCompilerAmbiguity",
    "BarrierFaceCompilerError",
    "BarrierFaceProgram",
    "BarrierFaceRewriteCandidate",
    "DEFAULT_PROGRAM",
    "apply_barrier_face_program",
    "compile_barrier_face_fill_rule",
    "face_has_majority_canvas_side",
    "select_minor_canvas_faces",
]
