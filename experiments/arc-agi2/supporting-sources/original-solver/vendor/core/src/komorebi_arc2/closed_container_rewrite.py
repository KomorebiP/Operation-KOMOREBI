"""Bounded causal rewrites over complete rectangular containers.

This module is intentionally independent of the main solver portfolio.  It
provides a small, auditable compiler that can later be adapted to the
``RuleCandidate`` interface without creating an import cycle.

The representation is input-only: a container is a complete, one-cell-thick,
monochrome rectangular perimeter.  Detection does not use connected
components, so a perimeter remains visible when unrelated packets of the same
colour occur elsewhere or touch its outside edge.  Demonstration outputs are
consulted only after the finite representation and renderer grammar have been
constructed.

The first grammar has one quantified selector, ``FOR_EACH``, and three atomic
renderers.  Every selected strict interior is filled with one demonstration-
derived colour.  The renderer may additionally erase the perimeter, or erase
both the perimeter and every exterior source-colour packet.  All writes are
computed from an immutable source raster and conflicting assignments cause an
explicit abstention.

Overlapping/nested/shared-wall rectangle interpretations, source-colour cells
inside a proposed strict interior, resource exhaustion, and a version-space
tie that changes held-out predictions are all abstention conditions.  This is
deliberately conservative: exact fit on demonstrations is necessary but not
sufficient when two causal programs remain distinguishable on the tests.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np

try:
    from .planar_incidence import AmbiguousBackgroundError, infer_background
except ImportError:  # standalone Kaggle runtime
    from planar_incidence import AmbiguousBackgroundError, infer_background


Array = np.ndarray
Cell = Tuple[int, int]
Box = Tuple[int, int, int, int]

CONTAINER_REWRITE_VERSION = "1.0"


class ClosedContainerError(ValueError):
    """Base class for explicit closed-container abstentions."""


class ClosedContainerAmbiguityError(ClosedContainerError):
    """Raised when cells admit incompatible container interpretations."""


class ClosedContainerLimitError(ClosedContainerError):
    """Raised before a configured representation budget is exceeded."""


class ClosedContainerConflictError(ClosedContainerError):
    """Raised when an atomic rewrite requests incompatible writes."""


@dataclass(frozen=True)
class ClosedContainerLimits:
    """Hard bounds for one input raster and its compiled version space."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_palette: int = 16
    maximum_rectangle_checks: int = 20_000
    maximum_raw_containers: int = 64
    maximum_containers: int = 32
    maximum_programs: int = 48


DEFAULT_LIMITS = ClosedContainerLimits()


@dataclass(frozen=True)
class ClosedContainer:
    """One complete monochrome rectangular perimeter found in an input."""

    color: int
    top: int
    left: int
    bottom: int
    right: int

    @property
    def box(self) -> Box:
        return self.top, self.left, self.bottom, self.right

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def interior_area(self) -> int:
        return max(0, self.height - 2) * max(0, self.width - 2)

    @property
    def perimeter_area(self) -> int:
        return 2 * self.height + 2 * self.width - 4

    def boundary_cells(self) -> Tuple[Cell, ...]:
        cells = set()
        for column in range(self.left, self.right + 1):
            cells.add((self.top, column))
            cells.add((self.bottom, column))
        for row in range(self.top, self.bottom + 1):
            cells.add((row, self.left))
            cells.add((row, self.right))
        return tuple(sorted(cells))

    def interior_cells(self) -> Tuple[Cell, ...]:
        return tuple(
            (row, column)
            for row in range(self.top + 1, self.bottom)
            for column in range(self.left + 1, self.right)
        )

    def json_record(self) -> Dict[str, object]:
        """Return coordinate-free structural facts suitable for provenance."""

        return {
            "boundary_color": int(self.color),
            "height": int(self.height),
            "width": int(self.width),
            "interior_area": int(self.interior_area),
            "perimeter_area": int(self.perimeter_area),
        }


_ERASE_SCOPES = (
    "preserve_boundary",
    "erase_boundary",
    "erase_boundary_and_exterior_source_color",
)


@dataclass(frozen=True)
class ClosedContainerProgram:
    """A coordinate-free, atomic ``FOR_EACH`` container rewrite."""

    fill_color: int
    erase_scope: str
    quantifier: str = "FOR_EACH"

    def __post_init__(self) -> None:
        if self.quantifier != "FOR_EACH":
            raise ClosedContainerError("the bounded compiler supports only FOR_EACH")
        if self.erase_scope not in _ERASE_SCOPES:
            raise ClosedContainerError(f"unknown erase scope {self.erase_scope!r}")

    @property
    def complexity(self) -> int:
        return 7 + _ERASE_SCOPES.index(self.erase_scope)

    @property
    def semantic_key(self) -> str:
        return (
            "closed_container|FOR_EACH|strict_interior|"
            f"fill:{int(self.fill_color)}|{self.erase_scope}"
        )

    def json_record(self) -> Dict[str, object]:
        return {
            "quantifier": self.quantifier,
            "selector": "all_unambiguous_complete_monochrome_rectangles",
            "interior_action": "fill_uniform_constant_role",
            "fill_color": int(self.fill_color),
            "erase_scope": self.erase_scope,
            "semantic_key": self.semantic_key,
        }


@dataclass(frozen=True)
class ClosedContainerTrace:
    """Aggregate effect evidence from one immutable-source application."""

    container_count: int
    changed_interior_cells: int
    changed_boundary_cells: int
    changed_exterior_source_color_cells: int
    requested_write_cells: int

    def json_record(self) -> Dict[str, int]:
        return {
            "container_count": int(self.container_count),
            "changed_interior_cells": int(self.changed_interior_cells),
            "changed_boundary_cells": int(self.changed_boundary_cells),
            "changed_exterior_source_color_cells": int(
                self.changed_exterior_source_color_cells
            ),
            "requested_write_cells": int(self.requested_write_cells),
        }


@dataclass(frozen=True)
class ClosedContainerRewriteCandidate:
    """Standalone candidate record consumed by a thin solver adapter."""

    name: str
    family: str
    complexity: int
    train_error: int
    program: ClosedContainerProgram
    train_grids: Tuple[Array, ...]
    grids: Tuple[Array, ...]
    metadata: Mapping[str, object]

    def json_record(self) -> Dict[str, object]:
        """Return a recursively JSON-safe record with no stored coordinates."""

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
        raise ClosedContainerError("container analysis requires a nonempty 2D grid")
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


def _runs(mask: Array) -> Iterable[Tuple[int, int]]:
    start: Optional[int] = None
    for index, raw in enumerate(np.asarray(mask, dtype=bool).tolist() + [False]):
        if raw and start is None:
            start = index
        elif not raw and start is not None:
            yield start, index - 1
            start = None


def _boxes_intersect(left: ClosedContainer, right: ClosedContainer) -> bool:
    return not (
        left.right < right.left
        or right.right < left.left
        or left.bottom < right.top
        or right.bottom < left.top
    )


def _validate_container_set(containers: Sequence[ClosedContainer]) -> None:
    if not containers:
        raise ClosedContainerError("no complete rectangular container")
    for index, left in enumerate(containers):
        if left.height < 3 or left.width < 3 or left.interior_area <= 0:
            raise ClosedContainerAmbiguityError("container has a vacuous interior")
        for right in containers[index + 1 :]:
            if _boxes_intersect(left, right):
                raise ClosedContainerAmbiguityError(
                    "container boxes overlap, nest, touch, or share a wall"
                )


def detect_closed_rectangular_containers(
    grid: Array,
    *,
    background: Optional[int] = None,
    limits: ClosedContainerLimits = DEFAULT_LIMITS,
) -> Tuple[ClosedContainer, ...]:
    """Detect an unambiguous set of complete monochrome rectangle perimeters.

    The search uses only the input raster.  Extra same-colour cells outside a
    rectangle do not invalidate it, including cells attached to its exterior.
    A same-colour cell in its strict interior does invalidate the scene: the
    proposed boundary then cannot be separated from an interior source packet
    by this deliberately narrow representation.
    """

    source = _grid(grid)
    height, width = source.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise ClosedContainerLimitError(
            f"grid {height}x{width} exceeds the configured container bound"
        )
    palette = tuple(int(value) for value in np.unique(source))
    if len(palette) > limits.maximum_palette:
        raise ClosedContainerLimitError("palette exceeds the configured bound")
    try:
        resolved_background = (
            infer_background(source) if background is None else int(background)
        )
    except AmbiguousBackgroundError as error:
        raise ClosedContainerAmbiguityError(str(error)) from error

    found: set[Tuple[int, int, int, int, int]] = set()
    checks = 0
    ambiguous_interior = False
    for color in palette:
        if color == resolved_background:
            continue
        color_mask = source == int(color)
        for top in range(height - 2):
            for bottom in range(top + 2, height):
                shared = color_mask[top, :] & color_mask[bottom, :]
                for run_left, run_right in _runs(shared):
                    if run_right - run_left < 2:
                        continue
                    for left in range(run_left, run_right - 1):
                        if not bool(np.all(color_mask[top : bottom + 1, left])):
                            continue
                        for right in range(left + 2, run_right + 1):
                            checks += 1
                            if checks > limits.maximum_rectangle_checks:
                                raise ClosedContainerLimitError(
                                    "rectangle-check budget exceeded"
                                )
                            if not bool(
                                np.all(color_mask[top : bottom + 1, right])
                            ):
                                continue
                            interior = color_mask[
                                top + 1 : bottom,
                                left + 1 : right,
                            ]
                            if bool(np.any(interior)):
                                ambiguous_interior = True
                                continue
                            found.add((color, top, left, bottom, right))
                            if len(found) > limits.maximum_raw_containers:
                                raise ClosedContainerLimitError(
                                    "raw-container budget exceeded"
                                )
    if len(found) > limits.maximum_containers:
        raise ClosedContainerLimitError("container budget exceeded")
    containers = tuple(
        ClosedContainer(color, top, left, bottom, right)
        for color, top, left, bottom, right in sorted(
            found,
            key=lambda item: (item[1], item[2], item[3], item[4], item[0]),
        )
    )
    if not containers and ambiguous_interior:
        raise ClosedContainerAmbiguityError(
            "a complete perimeter has source-colour cells in its strict interior"
        )
    _validate_container_set(containers)
    if ambiguous_interior:
        raise ClosedContainerAmbiguityError(
            "a complete perimeter has source-colour cells in its strict interior"
        )
    return containers


def _interior_union(
    shape: Tuple[int, int],
    containers: Sequence[ClosedContainer],
) -> Array:
    mask = np.zeros(shape, dtype=bool)
    for container in containers:
        mask[
            container.top + 1 : container.bottom,
            container.left + 1 : container.right,
        ] = True
    return mask


def apply_closed_container_program(
    grid: Array,
    program: ClosedContainerProgram,
    *,
    containers: Optional[Sequence[ClosedContainer]] = None,
    background: Optional[int] = None,
    limits: ClosedContainerLimits = DEFAULT_LIMITS,
) -> Tuple[Array, ClosedContainerTrace]:
    """Apply one program atomically and return its aggregate effect trace."""

    source = _grid(grid)
    try:
        resolved_background = (
            infer_background(source) if background is None else int(background)
        )
    except AmbiguousBackgroundError as error:
        raise ClosedContainerAmbiguityError(str(error)) from error
    selected = tuple(
        detect_closed_rectangular_containers(
            source,
            background=resolved_background,
            limits=limits,
        )
        if containers is None
        else containers
    )
    _validate_container_set(selected)

    assignments: Dict[Cell, int] = {}

    def assign(cell: Cell, value: int) -> None:
        previous = assignments.get(cell)
        if previous is not None and int(previous) != int(value):
            raise ClosedContainerConflictError(
                f"conflicting atomic writes at cell {cell!r}"
            )
        assignments[cell] = int(value)

    changed_interior = 0
    changed_boundary = 0
    changed_exterior = 0
    interior = _interior_union(source.shape, selected)
    for container in selected:
        local_changes = 0
        for cell in container.interior_cells():
            if int(source[cell]) != int(program.fill_color):
                local_changes += 1
                changed_interior += 1
            assign(cell, int(program.fill_color))
        # Filling each selected container must itself be a witnessed effect.
        # Otherwise boundary erasure could make an arbitrary latent rectangle
        # appear supported.
        if local_changes <= 0:
            raise ClosedContainerError("selected container has a vacuous fill effect")

    if program.erase_scope in {
        "erase_boundary",
        "erase_boundary_and_exterior_source_color",
    }:
        for container in selected:
            for cell in container.boundary_cells():
                if int(source[cell]) != resolved_background:
                    changed_boundary += 1
                assign(cell, resolved_background)

    if program.erase_scope == "erase_boundary_and_exterior_source_color":
        source_colors = {int(container.color) for container in selected}
        boundary = {
            cell for container in selected for cell in container.boundary_cells()
        }
        for raw_row, raw_column in np.argwhere(
            np.isin(source, tuple(sorted(source_colors))) & ~interior
        ):
            cell = (int(raw_row), int(raw_column))
            assign(cell, resolved_background)
            if cell not in boundary and int(source[cell]) != resolved_background:
                changed_exterior += 1

    if not assignments:
        raise ClosedContainerError("container program requested no writes")
    output = source.copy()
    for cell, value in sorted(assignments.items()):
        output[cell] = int(value)
    trace = ClosedContainerTrace(
        container_count=len(selected),
        changed_interior_cells=changed_interior,
        changed_boundary_cells=changed_boundary,
        changed_exterior_source_color_cells=changed_exterior,
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


def _aggregate_traces(traces: Sequence[ClosedContainerTrace]) -> Dict[str, int]:
    records = [trace.json_record() for trace in traces]
    return {
        "demonstrations": len(records),
        "selected_containers": sum(item["container_count"] for item in records),
        "multi_container_demonstrations": sum(
            item["container_count"] >= 2 for item in records
        ),
        "changed_interior_cells": sum(
            item["changed_interior_cells"] for item in records
        ),
        "changed_boundary_cells": sum(
            item["changed_boundary_cells"] for item in records
        ),
        "changed_exterior_source_color_cells": sum(
            item["changed_exterior_source_color_cells"] for item in records
        ),
        "requested_write_cells": sum(
            item["requested_write_cells"] for item in records
        ),
    }


def compile_closed_container_zone_rewrites(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: ClosedContainerLimits = DEFAULT_LIMITS,
) -> Tuple[ClosedContainerRewriteCandidate, ...]:
    """Compile an exact, bounded, ambiguity-safe container rewrite.

    Candidate geometry is computed from each source before the corresponding
    target is inspected.  The target contributes only a finite fill-colour
    role and exact-fit supervision over the three erase scopes.  If exact
    programs disagree on a held-out prediction, the compiler returns no
    candidate rather than choosing by complexity or palette order.
    """

    if not train or not tests:
        return ()
    try:
        normalized_train = tuple((_grid(source), _grid(target)) for source, target in train)
        normalized_tests = tuple(_grid(source) for source in tests)
        if not all(source.shape == target.shape for source, target in normalized_train):
            return ()
        # Freeze the input-only representation before using any target colour.
        train_containers = tuple(
            detect_closed_rectangular_containers(source, limits=limits)
            for source, _ in normalized_train
        )
        test_containers = tuple(
            detect_closed_rectangular_containers(source, limits=limits)
            for source in normalized_tests
        )
    except ClosedContainerError:
        return ()

    fill_colors = sorted(
        {
            int(value)
            for _, target in normalized_train
            for value in np.unique(target)
        }
    )
    if len(fill_colors) * len(_ERASE_SCOPES) > limits.maximum_programs:
        return ()

    exact_programs = []
    for fill_color in fill_colors:
        for erase_scope in _ERASE_SCOPES:
            program = ClosedContainerProgram(fill_color, erase_scope)
            try:
                train_results = tuple(
                    apply_closed_container_program(
                        source,
                        program,
                        containers=containers,
                        limits=limits,
                    )
                    for (source, _), containers in zip(
                        normalized_train,
                        train_containers,
                    )
                )
                train_predictions = tuple(item[0] for item in train_results)
                if not all(
                    np.array_equal(prediction, target)
                    for prediction, (_, target) in zip(
                        train_predictions,
                        normalized_train,
                    )
                ):
                    continue
                if any(
                    np.array_equal(source, target)
                    for source, target in normalized_train
                ):
                    continue
                test_results = tuple(
                    apply_closed_container_program(
                        source,
                        program,
                        containers=containers,
                        limits=limits,
                    )
                    for source, containers in zip(
                        normalized_tests,
                        test_containers,
                    )
                )
            except ClosedContainerError:
                continue
            exact_programs.append(
                (
                    program,
                    train_predictions,
                    tuple(item[0] for item in test_results),
                    tuple(item[1] for item in train_results),
                )
            )

    if not exact_programs:
        return ()
    prediction_groups: Dict[str, list[object]] = {}
    for record in exact_programs:
        prediction_groups.setdefault(_prediction_digest(record[2]), []).append(record)
    if len(prediction_groups) != 1:
        # An exact-demo version-space tie that matters on held-out inputs.
        return ()
    aliases = next(iter(prediction_groups.values()))
    chosen = min(
        aliases,
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )
    program, train_predictions, test_predictions, train_traces = chosen
    evidence = _aggregate_traces(train_traces)
    metadata: Dict[str, object] = {
        "compiler_block": "closed_container_zone_rewrite",
        "compiler_version": CONTAINER_REWRITE_VERSION,
        "typed_entity": "complete_monochrome_rectangular_perimeter",
        "representation_source": "input_only",
        "background_policy": "input_only_structural_inference",
        "selector": "all_unambiguous_complete_monochrome_rectangles",
        "quantifier": "FOR_EACH",
        "renderer": "atomic_closed_container_zone_rewrite",
        "interior_zone": "strict_interior",
        "interior_action": "fill_uniform_constant_role",
        "fill_color": int(program.fill_color),
        "erase_scope": program.erase_scope,
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
            "kind": "test_input_container_zone_transform",
            "geometry": "test_input_detected_containers",
            "color_role": "demonstration_derived_constant",
        },
        "provenance_kind": "test_input_structural_role_transform",
        "test_input_grounded": True,
        "permutation_invariant": True,
        "d4_equivariant": True,
        "task_palette_equivariant": True,
        "admissible": True,
        "partial_program": True,
        "stores_coordinates": False,
        "stores_training_rasters": False,
        "stores_task_ids": False,
        "exact_demonstration_contract": True,
        "resource_limits": {
            "maximum_height": int(limits.maximum_height),
            "maximum_width": int(limits.maximum_width),
            "maximum_palette": int(limits.maximum_palette),
            "maximum_rectangle_checks": int(limits.maximum_rectangle_checks),
            "maximum_raw_containers": int(limits.maximum_raw_containers),
            "maximum_containers": int(limits.maximum_containers),
            "maximum_programs": int(limits.maximum_programs),
        },
        "train_container_count_min": min(len(items) for items in train_containers),
        "train_container_count_max": max(len(items) for items in train_containers),
        "test_container_count_min": min(len(items) for items in test_containers),
        "test_container_count_max": max(len(items) for items in test_containers),
    }
    candidate = ClosedContainerRewriteCandidate(
        name=f"closed_container_{program.semantic_key}",
        family="causal_closed_container_zone_rewrite",
        complexity=program.complexity,
        train_error=0,
        program=program,
        train_grids=tuple(grid.copy() for grid in train_predictions),
        grids=tuple(grid.copy() for grid in test_predictions),
        metadata=metadata,
    )
    return (candidate,)


__all__ = [
    "CONTAINER_REWRITE_VERSION",
    "ClosedContainer",
    "ClosedContainerAmbiguityError",
    "ClosedContainerConflictError",
    "ClosedContainerError",
    "ClosedContainerLimitError",
    "ClosedContainerLimits",
    "ClosedContainerProgram",
    "ClosedContainerRewriteCandidate",
    "ClosedContainerTrace",
    "DEFAULT_LIMITS",
    "apply_closed_container_program",
    "compile_closed_container_zone_rewrites",
    "detect_closed_rectangular_containers",
]
