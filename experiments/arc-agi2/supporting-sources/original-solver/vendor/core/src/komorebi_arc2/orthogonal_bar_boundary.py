"""Source-local propagation of sparse defects across a thick orthogonal L.

The fixed program in this module recognizes a binary foreground whose latent
support is the union of one horizontal and one vertical filled rectangle.  The
rectangles meet at one end of each bar, forming a thick L.  Sparse source
defects may occur on a bar boundary or on the immediately adjacent exterior
layer.  Each defect is propagated to the opposite side of the same bar:

* a missing boundary cell paints the opposite exterior cell; and
* an exterior protrusion erases the opposite boundary cell.

Corner defects use the longest admissible bar axis.  The latent L is inferred
from the current source only.  The executor requires a unique minimum-residual
decomposition and commits all writes atomically.  Ambiguous, multicolour,
unbounded, dense-defect, or non-L scenes abstain.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]

SCHEMA = "komorebi.arc.orthogonal-bar-boundary-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_orthogonal_bar_boundary_complement"
OPERATOR = "propagate_sparse_l_bar_boundary_complements"


class OrthogonalBarError(ValueError):
    """Base class for invalid programs and source rasters."""


class OrthogonalBarAbstention(OrthogonalBarError):
    """Raised when no unique source-local L interpretation is available."""


class OrthogonalBarAmbiguityError(OrthogonalBarAbstention):
    """Raised when minimum-residual L interpretations are not unique."""


class OrthogonalBarLimitError(OrthogonalBarError):
    """Raised before a configured finite enumeration budget is exceeded."""


@dataclass(frozen=True)
class OrthogonalBarLimits:
    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_examples: int = 10
    maximum_tests: int = 8
    minimum_dimension: int = 8
    minimum_foreground_cells: int = 20
    minimum_bar_thickness: int = 3
    maximum_bar_thickness: int = 10
    minimum_defects: int = 2
    maximum_defects: int = 8
    minimum_area_per_defect: int = 8
    minimum_rectangle_fill_percent: int = 90
    minimum_defect_score_gap: int = 2
    maximum_hypotheses: int = 100_000

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise OrthogonalBarLimitError(f"{name} must be a positive integer")
        if self.minimum_bar_thickness > self.maximum_bar_thickness:
            raise OrthogonalBarLimitError(
                "minimum_bar_thickness exceeds maximum_bar_thickness"
            )
        if self.minimum_defects > self.maximum_defects:
            raise OrthogonalBarLimitError("minimum_defects exceeds maximum_defects")
        if self.minimum_rectangle_fill_percent > 100:
            raise OrthogonalBarLimitError(
                "minimum_rectangle_fill_percent cannot exceed 100"
            )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = OrthogonalBarLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def orthogonal_bar_implementation_fingerprint() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class OrthogonalBarBoundaryProgram:
    operator: str = OPERATOR
    domain: str = "binary_thick_l_union"
    background_policy: str = "unique_global_mode"
    decomposition_policy: str = "unique_minimum_residual"
    effect: str = "longest_axis_opposite_boundary_complement"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, (int, np.integer))
            or int(self.schema_version) != SCHEMA_VERSION
        ):
            raise OrthogonalBarError("unsupported orthogonal-bar schema version")
        expected = (
            OPERATOR,
            "binary_thick_l_union",
            "unique_global_mode",
            "unique_minimum_residual",
            "longest_axis_opposite_boundary_complement",
            SCHEMA_VERSION,
        )
        observed = (
            self.operator,
            self.domain,
            self.background_policy,
            self.decomposition_policy,
            self.effect,
            self.schema_version,
        )
        if observed != expected:
            raise OrthogonalBarError("unsupported orthogonal-bar program record")

    @classmethod
    def from_record(cls, raw: object) -> "OrthogonalBarBoundaryProgram":
        if not isinstance(raw, Mapping):
            raise OrthogonalBarError("program record must be a mapping")
        expected = {
            "schema",
            "schema_version",
            "operator",
            "domain",
            "background_policy",
            "decomposition_policy",
            "effect",
        }
        if set(raw) != expected or raw.get("schema") != SCHEMA:
            raise OrthogonalBarError("program record does not match schema")
        schema_version = raw["schema_version"]
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, (int, np.integer))
            or int(schema_version) != SCHEMA_VERSION
        ):
            raise OrthogonalBarError("program record has an invalid schema version")
        return cls(
            operator=str(raw["operator"]),
            domain=str(raw["domain"]),
            background_policy=str(raw["background_policy"]),
            decomposition_policy=str(raw["decomposition_policy"]),
            effect=str(raw["effect"]),
            schema_version=int(schema_version),
        )

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": self.operator,
            "domain": self.domain,
            "background_policy": self.background_policy,
            "decomposition_policy": self.decomposition_policy,
            "effect": self.effect,
        }
        _canonical_json(record)
        return record

    @property
    def semantic_key(self) -> str:
        return _canonical_json(self.to_record())

    def program_hash(self) -> str:
        return hashlib.sha256(self.semantic_key.encode("ascii")).hexdigest()

    @property
    def complexity(self) -> int:
        return 28

    def apply(
        self,
        grid: Array,
        *,
        limits: OrthogonalBarLimits = DEFAULT_LIMITS,
    ) -> Array:
        if type(self) is not OrthogonalBarBoundaryProgram:
            raise OrthogonalBarError("program subclasses are not executable records")
        self.__post_init__()
        return apply_orthogonal_bar_boundary_complement(grid, limits=limits)


@dataclass(frozen=True)
class OrthogonalBarTrace:
    source_shape: Tuple[int, int]
    horizontal_box: Box
    vertical_box: Box
    corner: str
    defect_cells: Tuple[Cell, ...]
    target_cells: Tuple[Cell, ...]
    missing_boundary_count: int
    exterior_protrusion_count: int
    hypothesis_count: int

    def to_record(self) -> Dict[str, object]:
        return {
            "source_shape": list(self.source_shape),
            "horizontal_box": list(self.horizontal_box),
            "vertical_box": list(self.vertical_box),
            "corner": self.corner,
            "defect_cells": [list(cell) for cell in self.defect_cells],
            "target_cells": [list(cell) for cell in self.target_cells],
            "missing_boundary_count": int(self.missing_boundary_count),
            "exterior_protrusion_count": int(self.exterior_protrusion_count),
            "hypothesis_count": int(self.hypothesis_count),
        }


@dataclass(frozen=True)
class OrthogonalBarCandidate:
    name: str
    program: OrthogonalBarBoundaryProgram
    grids: Tuple[Array, ...]
    train_grids: Tuple[Array, ...]
    train_error: int
    complexity: int
    family: str
    metadata: Mapping[str, object]


@dataclass(frozen=True)
class _Interpretation:
    output: Array
    horizontal_box: Box
    vertical_box: Box
    corner: str
    defects: Tuple[Cell, ...]
    targets: Tuple[Cell, ...]
    missing_boundary_count: int
    exterior_protrusion_count: int


def _validated_grid(grid: Array, limits: OrthogonalBarLimits) -> Array:
    try:
        raw = np.asarray(grid)
    except (TypeError, ValueError) as error:
        raise OrthogonalBarError("grid must be a rectangular numeric raster") from error
    if raw.ndim != 2 or raw.size == 0:
        raise OrthogonalBarError("grid must be a nonempty 2D raster")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise OrthogonalBarLimitError("grid shape exceeds configured limits")
    if raw.size > limits.maximum_cells:
        raise OrthogonalBarLimitError("grid cell budget exceeded")
    if np.issubdtype(raw.dtype, np.bool_):
        raise OrthogonalBarError("Boolean rasters are not ARC colour grids")
    if not np.issubdtype(raw.dtype, np.integer):
        try:
            if not bool(np.all(np.equal(raw, np.floor(raw)))):
                raise OrthogonalBarError("grid values must be integers")
        except (TypeError, ValueError) as error:
            raise OrthogonalBarError("grid values must be integers") from error
    try:
        minimum = int(np.min(raw))
        maximum = int(np.max(raw))
    except (TypeError, ValueError, OverflowError) as error:
        raise OrthogonalBarError("grid values must be finite integers") from error
    if minimum < 0 or maximum > 9:
        raise OrthogonalBarError("ARC colours must lie in [0, 9]")
    return np.ascontiguousarray(raw, dtype=np.int16)


def _binary_roles(grid: Array) -> Tuple[int, int, Array]:
    colors, counts = np.unique(grid, return_counts=True)
    if len(colors) != 2:
        raise OrthogonalBarAbstention("source must contain exactly two colours")
    maximum = int(counts.max())
    background_indices = np.flatnonzero(counts == maximum)
    if len(background_indices) != 1:
        raise OrthogonalBarAbstention("global-mode background is not unique")
    background_index = int(background_indices[0])
    foreground_index = 1 - background_index
    background = int(colors[background_index])
    foreground = int(colors[foreground_index])
    return background, foreground, np.ascontiguousarray(grid == foreground)


def _foreground_is_connected(mask: Array) -> bool:
    coordinates = np.argwhere(mask)
    if coordinates.size == 0:
        return False
    start = tuple(int(value) for value in coordinates[0])
    stack = [start]
    seen = {start}
    height, width = mask.shape
    while stack:
        row, column = stack.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nxt = row + dr, column + dc
            if (
                0 <= nxt[0] < height
                and 0 <= nxt[1] < width
                and bool(mask[nxt])
                and nxt not in seen
            ):
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == int(mask.sum())


def _near_extreme_range(value: int, lower: int, upper: int) -> range:
    start = max(lower, value - 1)
    stop = min(upper, value + 1)
    return range(start, stop + 1) if start <= stop else range(0)


def _counterparts(cell: Cell, boxes: Sequence[Box]) -> Tuple[Cell, ...]:
    row, column = cell
    found: list[Cell] = []
    for top, left, bottom, right in boxes:
        if left <= column <= right:
            if row == top - 1:
                found.append((bottom, column))
            if row == top:
                found.append((bottom + 1, column))
            if row == bottom:
                found.append((top - 1, column))
            if row == bottom + 1:
                found.append((top, column))
        if top <= row <= bottom:
            if column == left - 1:
                found.append((row, right))
            if column == left:
                found.append((row, right + 1))
            if column == right:
                found.append((row, left - 1))
            if column == right + 1:
                found.append((row, left))
    return tuple(dict.fromkeys(found))


def _interpretation(
    grid: Array,
    foreground_mask: Array,
    background: int,
    foreground: int,
    overall_box: Box,
    horizontal_thickness: int,
    vertical_thickness: int,
    horizontal_at_top: bool,
    vertical_at_left: bool,
    limits: OrthogonalBarLimits,
) -> Optional[_Interpretation]:
    top, left, bottom, right = overall_box
    horizontal_top = top if horizontal_at_top else bottom - horizontal_thickness + 1
    horizontal_bottom = horizontal_top + horizontal_thickness - 1
    vertical_left = left if vertical_at_left else right - vertical_thickness + 1
    vertical_right = vertical_left + vertical_thickness - 1
    horizontal_box = (horizontal_top, left, horizontal_bottom, right)
    vertical_box = (top, vertical_left, bottom, vertical_right)
    boxes = (horizontal_box, vertical_box)

    latent = np.zeros_like(foreground_mask, dtype=bool)
    latent[horizontal_top : horizontal_bottom + 1, left : right + 1] = True
    latent[top : bottom + 1, vertical_left : vertical_right + 1] = True
    horizontal_area = horizontal_thickness * (right - left + 1)
    vertical_area = vertical_thickness * (bottom - top + 1)
    horizontal_filled = int(
        foreground_mask[
            horizontal_top : horizontal_bottom + 1, left : right + 1
        ].sum()
    )
    vertical_filled = int(
        foreground_mask[top : bottom + 1, vertical_left : vertical_right + 1].sum()
    )
    if (
        100 * horizontal_filled
        < limits.minimum_rectangle_fill_percent * horizontal_area
        or 100 * vertical_filled
        < limits.minimum_rectangle_fill_percent * vertical_area
    ):
        return None
    defects_array = np.argwhere(foreground_mask != latent)
    defect_count = len(defects_array)
    latent_area = int(latent.sum())
    if not (
        limits.minimum_defects <= defect_count <= limits.maximum_defects
        and limits.minimum_area_per_defect * defect_count <= latent_area
    ):
        return None

    height, width = grid.shape
    defects = tuple(
        (int(row), int(column)) for row, column in defects_array.tolist()
    )
    targets: list[Cell] = []
    missing = 0
    protrusions = 0
    for defect in defects:
        source_value = bool(foreground_mask[defect])
        latent_value = bool(latent[defect])
        if source_value == latent_value:
            return None
        if source_value:
            protrusions += 1
        else:
            missing += 1
        options = []
        for target in _counterparts(defect, boxes):
            row, column = target
            if not (0 <= row < height and 0 <= column < width):
                continue
            if bool(foreground_mask[target]) != bool(latent[target]):
                continue
            if bool(latent[target]) != source_value:
                continue
            options.append(target)
        if not options:
            return None
        distances = [
            abs(target[0] - defect[0]) + abs(target[1] - defect[1])
            for target in options
        ]
        maximum_distance = max(distances)
        winners = tuple(
            target
            for target, distance in zip(options, distances)
            if distance == maximum_distance
        )
        if len(winners) != 1:
            return None
        targets.append(winners[0])

    if len(set(targets)) != len(targets):
        return None
    output = grid.copy()
    writes: Dict[Cell, int] = {}
    for target in targets:
        value = background if int(grid[target]) == foreground else foreground
        previous = writes.get(target)
        if previous is not None and previous != value:
            return None
        writes[target] = value
    if not writes:
        return None
    for target, value in writes.items():
        output[target] = value
    corner = ("top" if horizontal_at_top else "bottom") + "_" + (
        "left" if vertical_at_left else "right"
    )
    return _Interpretation(
        output=np.ascontiguousarray(output),
        horizontal_box=horizontal_box,
        vertical_box=vertical_box,
        corner=corner,
        defects=defects,
        targets=tuple(targets),
        missing_boundary_count=missing,
        exterior_protrusion_count=protrusions,
    )


def _enumerate_interpretations(
    grid: Array,
    background: int,
    foreground: int,
    foreground_mask: Array,
    limits: OrthogonalBarLimits,
) -> Tuple[_Interpretation, int]:
    coordinates = np.argwhere(foreground_mask)
    if coordinates.size == 0:
        raise OrthogonalBarAbstention("source has no foreground")
    foreground_top, foreground_left = (
        int(value) for value in coordinates.min(axis=0)
    )
    foreground_bottom, foreground_right = (
        int(value) for value in coordinates.max(axis=0)
    )
    height, width = grid.shape
    interpretations: list[_Interpretation] = []
    hypothesis_count = 0
    for top in _near_extreme_range(foreground_top, 1, height - 4):
        for bottom in _near_extreme_range(
            foreground_bottom, top + 3, height - 2
        ):
            overall_height = bottom - top + 1
            for left in _near_extreme_range(foreground_left, 1, width - 4):
                for right in _near_extreme_range(
                    foreground_right, left + 3, width - 2
                ):
                    overall_width = right - left + 1
                    maximum_horizontal = min(
                        limits.maximum_bar_thickness, overall_height - 1
                    )
                    maximum_vertical = min(
                        limits.maximum_bar_thickness, overall_width - 1
                    )
                    for horizontal_thickness in range(
                        limits.minimum_bar_thickness, maximum_horizontal + 1
                    ):
                        if overall_width < 2 * horizontal_thickness:
                            continue
                        for vertical_thickness in range(
                            limits.minimum_bar_thickness, maximum_vertical + 1
                        ):
                            if overall_height < 2 * vertical_thickness:
                                continue
                            for horizontal_at_top in (True, False):
                                for vertical_at_left in (True, False):
                                    hypothesis_count += 1
                                    if hypothesis_count > limits.maximum_hypotheses:
                                        raise OrthogonalBarLimitError(
                                            "L-decomposition hypothesis budget exceeded"
                                        )
                                    candidate = _interpretation(
                                        grid,
                                        foreground_mask,
                                        background,
                                        foreground,
                                        (top, left, bottom, right),
                                        horizontal_thickness,
                                        vertical_thickness,
                                        horizontal_at_top,
                                        vertical_at_left,
                                        limits,
                                    )
                                    if candidate is not None:
                                        interpretations.append(candidate)
    if not interpretations:
        raise OrthogonalBarAbstention("no admissible thick-L decomposition")
    minimum_defects = min(len(item.defects) for item in interpretations)
    best = tuple(
        item for item in interpretations if len(item.defects) == minimum_defects
    )
    if len(best) != 1:
        raise OrthogonalBarAmbiguityError(
            "minimum-residual thick-L decomposition is not unique"
        )
    distinct_scores = sorted({len(item.defects) for item in interpretations})
    if (
        len(distinct_scores) > 1
        and distinct_scores[1] - distinct_scores[0]
        < limits.minimum_defect_score_gap
    ):
        raise OrthogonalBarAmbiguityError(
            "minimum-residual thick-L decomposition lacks a score gap"
        )
    return best[0], hypothesis_count


def apply_orthogonal_bar_boundary_complement_with_trace(
    grid: Array,
    *,
    limits: OrthogonalBarLimits = DEFAULT_LIMITS,
) -> Tuple[Array, OrthogonalBarTrace]:
    source = _validated_grid(grid, limits)
    if min(source.shape) < limits.minimum_dimension:
        raise OrthogonalBarAbstention("source is too small for a thick-L scene")
    background, foreground, foreground_mask = _binary_roles(source)
    if int(foreground_mask.sum()) < limits.minimum_foreground_cells:
        raise OrthogonalBarAbstention("foreground support is too small")
    if not _foreground_is_connected(foreground_mask):
        raise OrthogonalBarAbstention("foreground is not one 4-connected packet")
    interpretation, hypothesis_count = _enumerate_interpretations(
        source,
        background,
        foreground,
        foreground_mask,
        limits,
    )
    trace = OrthogonalBarTrace(
        source_shape=tuple(int(value) for value in source.shape),
        horizontal_box=interpretation.horizontal_box,
        vertical_box=interpretation.vertical_box,
        corner=interpretation.corner,
        defect_cells=interpretation.defects,
        target_cells=interpretation.targets,
        missing_boundary_count=interpretation.missing_boundary_count,
        exterior_protrusion_count=interpretation.exterior_protrusion_count,
        hypothesis_count=hypothesis_count,
    )
    return interpretation.output, trace


def apply_orthogonal_bar_boundary_complement(
    grid: Array,
    *,
    limits: OrthogonalBarLimits = DEFAULT_LIMITS,
) -> Array:
    output, _ = apply_orthogonal_bar_boundary_complement_with_trace(
        grid, limits=limits
    )
    return output


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def compile_orthogonal_bar_boundary_complement(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: OrthogonalBarLimits = DEFAULT_LIMITS,
) -> Tuple[OrthogonalBarCandidate, ...]:
    """Expose the fixed program only after exact distinct-example replay."""

    if len(train) < 3 or not tests:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise OrthogonalBarLimitError("example budget exceeded")
    groups: Dict[str, Tuple[Array, Array]] = {}
    validated: list[Tuple[Array, Array]] = []
    for raw_source, raw_target in train:
        source = _validated_grid(raw_source, limits)
        target = _validated_grid(raw_target, limits)
        if np.array_equal(source, target):
            return ()
        key = _example_hash(source, target)
        groups.setdefault(key, (source, target))
        validated.append((source, target))
    if len(groups) < 2:
        return ()

    program = OrthogonalBarBoundaryProgram()
    train_predictions: list[Array] = []
    traces: list[OrthogonalBarTrace] = []
    try:
        for source, target in validated:
            prediction, trace = apply_orthogonal_bar_boundary_complement_with_trace(
                source, limits=limits
            )
            if not np.array_equal(prediction, target):
                return ()
            train_predictions.append(prediction)
            traces.append(trace)
    except OrthogonalBarAbstention:
        return ()

    # The demonstrations must witness both semantic directions.  This rejects
    # construction-only or erasure-only tasks that happen to share an L mask.
    if not all(
        trace.missing_boundary_count > 0
        and trace.exterior_protrusion_count > 0
        for trace in traces
    ):
        return ()

    try:
        test_predictions = tuple(
            program.apply(test, limits=limits) for test in tests
        )
    except OrthogonalBarAbstention:
        return ()
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.orthogonal-bar-boundary-candidate.v1",
        "program": program.to_record(),
        "program_hash": program.program_hash(),
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "literal_color_free_program": True,
        "literal_coordinate_free_program": True,
        "raw_grid_free_program": True,
        "palette_equivariant": True,
        "d4_equivariant": True,
        "atomic_collision_abstention": True,
        "unique_source_decomposition": True,
        "distinct_witness_groups": int(len(groups)),
        "loo_exact_count": int(len(groups)),
        "loo_total_count": int(len(groups)),
        "witness_protocol": "fixed_program_distinct_group_replay",
        "both_defect_polarities_witnessed": True,
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": orthogonal_bar_implementation_fingerprint(),
        "limits": limits.to_record(),
    }
    candidate = OrthogonalBarCandidate(
        name=f"orthogonal_bar_boundary:{program.program_hash()[:12]}",
        program=program,
        grids=tuple(np.ascontiguousarray(grid) for grid in test_predictions),
        train_grids=tuple(np.ascontiguousarray(grid) for grid in train_predictions),
        train_error=0,
        complexity=program.complexity,
        family=FAMILY,
        metadata=metadata,
    )
    return (candidate,)


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "OPERATOR",
    "OrthogonalBarAbstention",
    "OrthogonalBarAmbiguityError",
    "OrthogonalBarBoundaryProgram",
    "OrthogonalBarCandidate",
    "OrthogonalBarError",
    "OrthogonalBarLimitError",
    "OrthogonalBarLimits",
    "OrthogonalBarTrace",
    "apply_orthogonal_bar_boundary_complement",
    "apply_orthogonal_bar_boundary_complement_with_trace",
    "compile_orthogonal_bar_boundary_complement",
    "orthogonal_bar_implementation_fingerprint",
]
