"""Typed relocation of a singleton marker onto an object-boundary run.

The interpreter binds three scene roles without task identifiers or fixed
palette values: a unique global-mode background, one singleton marker colour,
and one remaining connected object colour.  It enumerates maximal straight
runs of background cells that are cardinally adjacent to the object.  The run
nearest the marker is selected, with longer runs preferred.  Axis-aligned runs
receive the marker at their nearest endpoint, while diagonal runs receive it
at their farthest endpoint.  Any unresolved structural tie causes abstention.

The compiler admits the parameter-free program only after exact demonstration
replay, three distinct witness groups, individual leave-one-out reinduction,
distinct-group leave-one-out reinduction, and evidence for both endpoint
policies.  The persistent program contains no colour, coordinate, raster, task
identifier, object size, or answer payload.
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
Direction = Tuple[int, int]

SCHEMA = "komorebi.arc.boundary-run-marker-relocation-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_boundary_run_marker_relocation"
OPERATOR = "relocate_singleton_marker_to_selected_boundary_run_endpoint"


class BoundaryRunMarkerRelocationError(ValueError):
    """Base class for invalid programs and explicit abstentions."""


class BoundaryRunMarkerRelocationAbstention(
    BoundaryRunMarkerRelocationError
):
    """Raised when the scene has no unique protected interpretation."""


class BoundaryRunMarkerRelocationLimitError(
    BoundaryRunMarkerRelocationError
):
    """Raised before a finite representation budget is exceeded."""


@dataclass(frozen=True)
class BoundaryRunMarkerRelocationLimits:
    """Hard bounds for the standalone compiler and interpreter."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_boundary_cells: int = 900
    maximum_runs: int = 3600
    maximum_examples: int = 10
    maximum_tests: int = 8

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise BoundaryRunMarkerRelocationLimitError(
                    f"{name} must be a positive integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = BoundaryRunMarkerRelocationLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def boundary_run_marker_relocation_implementation_fingerprint() -> str:
    """Hash the exact standalone compiler and interpreter source."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class BoundaryRunMarkerRelocationProgram:
    """Canonical parameter-free boundary-run relocation program."""

    operator: str = OPERATOR
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise BoundaryRunMarkerRelocationError(
                f"unsupported schema version {self.schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )
        if self.operator != OPERATOR:
            raise BoundaryRunMarkerRelocationError(
                f"unknown boundary-run operator {self.operator!r}"
            )

    @classmethod
    def from_record(
        cls,
        raw: object,
    ) -> "BoundaryRunMarkerRelocationProgram":
        if not isinstance(raw, Mapping):
            raise BoundaryRunMarkerRelocationError(
                "boundary-run program must be a mapping"
            )
        expected = {"schema", "schema_version", "operator"}
        present = set(raw)
        if present != expected:
            raise BoundaryRunMarkerRelocationError(
                "boundary-run program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise BoundaryRunMarkerRelocationError(
                f"unknown boundary-run schema {raw['schema']!r}"
            )
        return cls(
            operator=str(raw["operator"]),
            schema_version=int(raw["schema_version"]),
        )

    def to_record(self) -> Dict[str, object]:
        record: Dict[str, object] = {
            "schema": SCHEMA,
            "schema_version": int(self.schema_version),
            "operator": str(self.operator),
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
        return 19

    def apply(
        self,
        grid: Array,
        *,
        limits: BoundaryRunMarkerRelocationLimits = DEFAULT_LIMITS,
    ) -> Array:
        return execute_boundary_run_marker_relocation_program(
            self,
            grid,
            limits=limits,
        )


@dataclass(frozen=True)
class _SceneRoles:
    background_color: int
    object_color: int
    marker_color: int
    marker_cell: Cell
    object_cell_count: int


@dataclass(frozen=True)
class _BoundaryRun:
    direction: Direction
    cells: Tuple[Cell, ...]

    @property
    def orientation_class(self) -> str:
        row_delta, column_delta = self.direction
        return (
            "diagonal"
            if row_delta != 0 and column_delta != 0
            else "axis"
        )


@dataclass(frozen=True)
class BoundaryRunMarkerRelocationTrace:
    """Coordinate-free runtime evidence for one source interpretation."""

    background_color: int
    object_color: int
    marker_color: int
    object_cell_count: int
    boundary_cell_count: int
    straight_run_count: int
    selected_run_length: int
    selected_orientation_class: str
    endpoint_policy: str
    selected_run_minimum_marker_distance: int
    destination_marker_distance: int

    def to_record(self) -> Dict[str, object]:
        return {
            "background_color": int(self.background_color),
            "object_color": int(self.object_color),
            "marker_color": int(self.marker_color),
            "object_cell_count": int(self.object_cell_count),
            "boundary_cell_count": int(self.boundary_cell_count),
            "straight_run_count": int(self.straight_run_count),
            "selected_run_length": int(self.selected_run_length),
            "selected_orientation_class": str(
                self.selected_orientation_class
            ),
            "endpoint_policy": str(self.endpoint_policy),
            "selected_run_minimum_marker_distance": int(
                self.selected_run_minimum_marker_distance
            ),
            "destination_marker_distance": int(
                self.destination_marker_distance
            ),
        }


@dataclass(frozen=True)
class MarkerMoveWitness:
    """Per-demonstration proof that the output is one marker relocation."""

    background_color: int
    object_color: int
    marker_color: int
    changed_cell_count: int
    selected_orientation_class: str
    endpoint_policy: str

    def to_record(self) -> Dict[str, object]:
        return {
            "background_color": int(self.background_color),
            "object_color": int(self.object_color),
            "marker_color": int(self.marker_color),
            "changed_cell_count": int(self.changed_cell_count),
            "selected_orientation_class": str(
                self.selected_orientation_class
            ),
            "endpoint_policy": str(self.endpoint_policy),
            "singleton_marker_erased_to_background": True,
            "destination_background_repainted_as_marker": True,
            "object_preserved": True,
            "palette_preserved": True,
        }


@dataclass(frozen=True)
class BoundaryRunMarkerRelocationCandidate:
    """Entry-independent exact candidate with canonical provenance."""

    name: str
    program: BoundaryRunMarkerRelocationProgram
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
            record["grids"] = [
                grid.astype(int).tolist() for grid in self.grids
            ]
            record["train_grids"] = [
                grid.astype(int).tolist() for grid in self.train_grids
            ]
        _canonical_json(record)
        return record


def _validated_grid(
    grid: Array,
    limits: BoundaryRunMarkerRelocationLimits,
) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise BoundaryRunMarkerRelocationAbstention(
            "grid must be a nonempty matrix"
        )
    if not np.issubdtype(raw.dtype, np.integer):
        raise BoundaryRunMarkerRelocationAbstention(
            "grid values must be integers"
        )
    values = np.asarray(raw, dtype=np.int64)
    height, width = values.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or values.size > limits.maximum_cells
    ):
        raise BoundaryRunMarkerRelocationLimitError(
            "grid exceeds ARC representation limits"
        )
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise BoundaryRunMarkerRelocationLimitError(
            "palette exceeds representation limit"
        )
    if np.any(palette < 0) or np.any(palette > 9):
        raise BoundaryRunMarkerRelocationAbstention(
            "grid colors must lie in the ARC palette"
        )
    return values.copy()


def _four_connected_component_count(
    source: Array,
    color: int,
) -> int:
    height, width = source.shape
    cells = {
        (int(row), int(column))
        for row, column in np.argwhere(source == color)
    }
    count = 0
    while cells:
        count += 1
        stack = [cells.pop()]
        while stack:
            row, column = stack.pop()
            for delta_row, delta_column in (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ):
                neighbor = (row + delta_row, column + delta_column)
                if neighbor in cells:
                    cells.remove(neighbor)
                    stack.append(neighbor)
    return count


def _bind_roles(source: Array) -> _SceneRoles:
    colors, counts = np.unique(source, return_counts=True)
    if len(colors) != 3:
        raise BoundaryRunMarkerRelocationAbstention(
            "scene must contain exactly background, object, and marker colors"
        )
    maximum = int(counts.max())
    background_indices = np.flatnonzero(counts == maximum)
    if len(background_indices) != 1:
        raise BoundaryRunMarkerRelocationAbstention(
            "global background mode is not unique"
        )
    background_color = int(colors[int(background_indices[0])])
    foreground = [
        (int(color), int(count))
        for color, count in zip(colors, counts)
        if int(color) != background_color
    ]
    singleton = [color for color, count in foreground if count == 1]
    nonsingleton = [
        (color, count) for color, count in foreground if count >= 2
    ]
    if len(singleton) != 1 or len(nonsingleton) != 1:
        raise BoundaryRunMarkerRelocationAbstention(
            "foreground roles require one singleton marker and one object"
        )
    marker_color = singleton[0]
    object_color, object_cell_count = nonsingleton[0]
    marker_positions = np.argwhere(source == marker_color)
    if len(marker_positions) != 1:
        raise BoundaryRunMarkerRelocationAbstention(
            "marker role is not uniquely bound"
        )
    if _four_connected_component_count(source, object_color) != 1:
        raise BoundaryRunMarkerRelocationAbstention(
            "object role must be one four-connected component"
        )
    marker_cell = tuple(int(value) for value in marker_positions[0])
    return _SceneRoles(
        background_color=background_color,
        object_color=object_color,
        marker_color=marker_color,
        marker_cell=marker_cell,
        object_cell_count=object_cell_count,
    )


def _boundary_cells(
    source: Array,
    roles: _SceneRoles,
    limits: BoundaryRunMarkerRelocationLimits,
) -> frozenset[Cell]:
    height, width = source.shape
    output: set[Cell] = set()
    for row in range(height):
        for column in range(width):
            if int(source[row, column]) != roles.background_color:
                continue
            for delta_row, delta_column in (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ):
                neighbor_row = row + delta_row
                neighbor_column = column + delta_column
                if (
                    0 <= neighbor_row < height
                    and 0 <= neighbor_column < width
                    and int(source[neighbor_row, neighbor_column])
                    == roles.object_color
                ):
                    output.add((row, column))
                    break
    if len(output) > limits.maximum_boundary_cells:
        raise BoundaryRunMarkerRelocationLimitError(
            "boundary-cell count exceeds representation limit"
        )
    if not output:
        raise BoundaryRunMarkerRelocationAbstention(
            "object has no in-bounds background boundary"
        )
    if roles.marker_cell in output:
        raise BoundaryRunMarkerRelocationAbstention(
            "source marker already occupies an object-boundary role"
        )
    return frozenset(output)


def _straight_runs(
    boundary: frozenset[Cell],
    limits: BoundaryRunMarkerRelocationLimits,
) -> Tuple[_BoundaryRun, ...]:
    directions: Tuple[Direction, ...] = (
        (0, 1),
        (1, 0),
        (1, 1),
        (1, -1),
    )
    output = []
    for direction in directions:
        delta_row, delta_column = direction
        for row, column in sorted(boundary):
            predecessor = (row - delta_row, column - delta_column)
            if predecessor in boundary:
                continue
            run = []
            current = (row, column)
            while current in boundary:
                run.append(current)
                current = (
                    current[0] + delta_row,
                    current[1] + delta_column,
                )
            if len(run) >= 2:
                output.append(
                    _BoundaryRun(direction=direction, cells=tuple(run))
                )
                if len(output) > limits.maximum_runs:
                    raise BoundaryRunMarkerRelocationLimitError(
                        "straight-run count exceeds representation limit"
                    )
    if not output:
        raise BoundaryRunMarkerRelocationAbstention(
            "boundary has no straight run of length at least two"
        )
    return tuple(output)


def _manhattan(first: Cell, second: Cell) -> int:
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def _destination_for_run(
    run: _BoundaryRun,
    marker: Cell,
) -> Tuple[Cell, str, int]:
    endpoints = (run.cells[0], run.cells[-1])
    distances = tuple(_manhattan(endpoint, marker) for endpoint in endpoints)
    if distances[0] == distances[1]:
        raise BoundaryRunMarkerRelocationAbstention(
            "selected run has an unresolved endpoint tie"
        )
    if run.orientation_class == "diagonal":
        index = 0 if distances[0] > distances[1] else 1
        policy = "farthest_endpoint"
    else:
        index = 0 if distances[0] < distances[1] else 1
        policy = "nearest_endpoint"
    return endpoints[index], policy, int(distances[index])


def _select_run(
    runs: Sequence[_BoundaryRun],
    marker: Cell,
) -> Tuple[_BoundaryRun, Cell, str, int, int]:
    scored = []
    for run in runs:
        minimum_distance = min(
            _manhattan(cell, marker) for cell in run.cells
        )
        scored.append((minimum_distance, -len(run.cells), run))
    best_key = min((distance, negative_length) for distance, negative_length, _ in scored)
    best_runs = [
        run
        for distance, negative_length, run in scored
        if (distance, negative_length) == best_key
    ]
    interpretations = []
    for run in best_runs:
        destination, policy, destination_distance = _destination_for_run(
            run,
            marker,
        )
        interpretations.append(
            (run, destination, policy, destination_distance)
        )
    destination_set = {item[1] for item in interpretations}
    policy_set = {item[2] for item in interpretations}
    if len(destination_set) != 1 or len(policy_set) != 1:
        raise BoundaryRunMarkerRelocationAbstention(
            "nearest boundary-run selection is structurally ambiguous"
        )
    chosen = min(
        interpretations,
        key=lambda item: (
            item[0].orientation_class,
            item[0].cells,
            item[0].direction,
        ),
    )
    run, destination, policy, destination_distance = chosen
    return (
        run,
        destination,
        policy,
        int(best_key[0]),
        int(destination_distance),
    )


def _execute_with_trace(
    program: BoundaryRunMarkerRelocationProgram,
    grid: Array,
    limits: BoundaryRunMarkerRelocationLimits,
) -> Tuple[Array, BoundaryRunMarkerRelocationTrace]:
    del program
    source = _validated_grid(grid, limits)
    roles = _bind_roles(source)
    boundary = _boundary_cells(source, roles, limits)
    runs = _straight_runs(boundary, limits)
    (
        selected,
        destination,
        endpoint_policy,
        minimum_distance,
        destination_distance,
    ) = _select_run(runs, roles.marker_cell)
    if destination == roles.marker_cell:
        raise BoundaryRunMarkerRelocationAbstention(
            "marker relocation would be an identity"
        )
    if int(source[destination]) != roles.background_color:
        raise BoundaryRunMarkerRelocationAbstention(
            "selected destination is not background"
        )
    output = source.copy()
    output[roles.marker_cell] = roles.background_color
    output[destination] = roles.marker_color
    trace = BoundaryRunMarkerRelocationTrace(
        background_color=roles.background_color,
        object_color=roles.object_color,
        marker_color=roles.marker_color,
        object_cell_count=roles.object_cell_count,
        boundary_cell_count=len(boundary),
        straight_run_count=len(runs),
        selected_run_length=len(selected.cells),
        selected_orientation_class=selected.orientation_class,
        endpoint_policy=endpoint_policy,
        selected_run_minimum_marker_distance=minimum_distance,
        destination_marker_distance=destination_distance,
    )
    return output, trace


def execute_boundary_run_marker_relocation_program(
    program: BoundaryRunMarkerRelocationProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: BoundaryRunMarkerRelocationLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind scene roles and execute one atomic marker relocation."""

    if not isinstance(program, BoundaryRunMarkerRelocationProgram):
        program = BoundaryRunMarkerRelocationProgram.from_record(program)
    output, _ = _execute_with_trace(program, grid, limits)
    return output.copy()


def _example_hash(source: Array, target: Array) -> str:
    digest = hashlib.sha256()
    for grid in (source, target):
        value = np.asarray(grid, dtype=np.int16)
        digest.update(np.asarray(value.shape, dtype=np.int16).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _move_witness(
    source: Array,
    target: Array,
    limits: BoundaryRunMarkerRelocationLimits,
) -> Optional[
    Tuple[
        BoundaryRunMarkerRelocationProgram,
        Array,
        BoundaryRunMarkerRelocationTrace,
        MarkerMoveWitness,
    ]
]:
    if source.shape != target.shape:
        return None
    try:
        roles = _bind_roles(source)
    except BoundaryRunMarkerRelocationAbstention:
        return None
    changed = np.argwhere(source != target)
    if len(changed) != 2:
        return None
    marker_cell = roles.marker_cell
    if int(target[marker_cell]) != roles.background_color:
        return None
    destinations = [
        (int(row), int(column))
        for row, column in changed
        if (int(row), int(column)) != marker_cell
    ]
    if len(destinations) != 1:
        return None
    destination = destinations[0]
    if not (
        int(source[destination]) == roles.background_color
        and int(target[destination]) == roles.marker_color
    ):
        return None
    if set(int(value) for value in np.unique(source)) != set(
        int(value) for value in np.unique(target)
    ):
        return None
    if not np.array_equal(
        source == roles.object_color,
        target == roles.object_color,
    ):
        return None
    program = BoundaryRunMarkerRelocationProgram()
    try:
        prediction, trace = _execute_with_trace(program, source, limits)
    except BoundaryRunMarkerRelocationAbstention:
        return None
    if not np.array_equal(prediction, target):
        return None
    witness = MarkerMoveWitness(
        background_color=roles.background_color,
        object_color=roles.object_color,
        marker_color=roles.marker_color,
        changed_cell_count=len(changed),
        selected_orientation_class=trace.selected_orientation_class,
        endpoint_policy=trace.endpoint_policy,
    )
    return program, prediction, trace, witness


def _infer_exact_program(
    train: Sequence[Tuple[Array, Array]],
    limits: BoundaryRunMarkerRelocationLimits,
) -> Optional[
    Tuple[
        BoundaryRunMarkerRelocationProgram,
        Tuple[Array, ...],
        Tuple[BoundaryRunMarkerRelocationTrace, ...],
        Tuple[MarkerMoveWitness, ...],
    ]
]:
    if not train:
        return None
    programs = []
    predictions = []
    traces = []
    witnesses = []
    for source, target in train:
        result = _move_witness(source, target, limits)
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


def compile_boundary_run_marker_relocation_program(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: BoundaryRunMarkerRelocationLimits = DEFAULT_LIMITS,
) -> Tuple[BoundaryRunMarkerRelocationCandidate, ...]:
    """Compile the fixed schema after exact replay and protected LOO."""

    if len(train) < 3:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise BoundaryRunMarkerRelocationLimitError(
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
    except BoundaryRunMarkerRelocationAbstention:
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 3:
        return ()

    full = _infer_exact_program(validated, limits)
    if full is None:
        return ()
    program, train_predictions, traces, witnesses = full
    program_hash = program.program_hash()

    orientation_classes = {
        trace.selected_orientation_class for trace in traces
    }
    endpoint_policies = {trace.endpoint_policy for trace in traces}
    if orientation_classes != {"axis", "diagonal"}:
        return ()
    if endpoint_policies != {"nearest_endpoint", "farthest_endpoint"}:
        return ()

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
        except BoundaryRunMarkerRelocationAbstention:
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
        except BoundaryRunMarkerRelocationAbstention:
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
    except BoundaryRunMarkerRelocationAbstention:
        return ()

    trace_records = [trace.to_record() for trace in traces]
    witness_records = [witness.to_record() for witness in witnesses]
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.boundary-run-marker-relocation-candidate.v1",
        "program": program.to_record(),
        "program_hash": program_hash,
        "semantic_key": program.semantic_key,
        "operator": OPERATOR,
        "domain": "one_connected_object_plus_one_singleton_marker",
        "background_binding": "unique_global_mode",
        "object_binding": "only_nonsingleton_nonbackground_color",
        "marker_binding": "only_singleton_nonbackground_color",
        "boundary_definition": (
            "background_cells_cardinally_adjacent_to_object"
        ),
        "run_directions": ["horizontal", "vertical", "diagonal_both_slopes"],
        "run_selector": "minimum_marker_distance_then_maximum_length",
        "tie_policy": "abstain_unless_all_best_runs_imply_same_destination",
        "axis_endpoint_policy": "nearest_endpoint",
        "diagonal_endpoint_policy": "farthest_endpoint",
        "effect": "erase_source_marker_and_repaint_selected_boundary_endpoint",
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "raw_grid_free_program": True,
        "literal_coordinate_free_program": True,
        "fixed_color_free_program": True,
        "object_size_free_program": True,
        "palette_equivariant": True,
        "d4_equivariant": True,
        "quarter_turn_equivariant": True,
        "both_orientation_classes_witnessed": True,
        "both_endpoint_policies_witnessed": True,
        "marker_move_witness": {
            "per_example": witness_records,
            "changed_cells_per_example": 2,
            "palette_preserved": True,
            "object_preserved": True,
        },
        "witness_protocol": (
            "full_demonstration_and_distinct_group_loo_reinduction"
        ),
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
        "complete_public_training_activation_scan": False,
        "external_gain_loss_audit": False,
        "development_evidence_scope": (
            "exact_public_training_fixture_plus_synthetic_invariance_tests"
        ),
        "implementation_fingerprint": (
            boundary_run_marker_relocation_implementation_fingerprint()
        ),
        "limits": limits.to_record(),
    }
    return (
        BoundaryRunMarkerRelocationCandidate(
            name=(
                "boundary_run_marker_relocation:selected_endpoint:"
                f"{program_hash[:12]}"
            ),
            program=program,
            grids=test_predictions,
            train_grids=train_predictions,
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


boundary_run_marker_relocation_candidates = (
    compile_boundary_run_marker_relocation_program
)


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "OPERATOR",
    "BoundaryRunMarkerRelocationAbstention",
    "BoundaryRunMarkerRelocationCandidate",
    "BoundaryRunMarkerRelocationError",
    "BoundaryRunMarkerRelocationLimitError",
    "BoundaryRunMarkerRelocationLimits",
    "BoundaryRunMarkerRelocationProgram",
    "BoundaryRunMarkerRelocationTrace",
    "MarkerMoveWitness",
    "boundary_run_marker_relocation_candidates",
    "boundary_run_marker_relocation_implementation_fingerprint",
    "compile_boundary_run_marker_relocation_program",
    "execute_boundary_run_marker_relocation_program",
]
