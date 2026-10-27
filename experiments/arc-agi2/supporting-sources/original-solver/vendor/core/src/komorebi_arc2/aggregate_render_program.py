"""Bounded aggregate-to-render programs for ARC scenes and row sequences.

This module contains three fixed, task-identifier-free programs:

* emit the unique foreground colour that owns a complete input row or column;
* retain every maximum-area monochrome component and serialize its colours as
  left-to-right solid columns whose height is the shared maximum area; and
* continue an exact row-block translation recurrence to a square canvas.

Programs store only a named structural operator.  Resolved colours, component
coordinates, recurrence parameters, task identifiers, and rasters are rebound
from each input at execution time.  Compilation requires exact demonstration
replay, distinct-example leave-one-group-out rediscovery of the same canonical
program, and unanimous predictions from every full-data-exact program.

The module is intentionally separate from role_bound_object_program.  That
interpreter has pinned empirical promotion evidence, so extending it in place
would invalidate previously audited programs before a new corpus audit exists.
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

SCHEMA = "komorebi.arc.aggregate-render-program.v1"
SCHEMA_VERSION = 1
FAMILY = "causal_aggregate_render"

UNIQUE_SPANNING_COLOR_SCALAR = "emit_unique_spanning_color_scalar"
MAX_AREA_COMPONENT_COLUMNS = "pack_max_area_component_color_columns"
ROW_TRANSLATION_RECURRENCE_SQUARE = "continue_row_translation_recurrence_square"

_OPERATORS = (
    UNIQUE_SPANNING_COLOR_SCALAR,
    MAX_AREA_COMPONENT_COLUMNS,
    ROW_TRANSLATION_RECURRENCE_SQUARE,
)
_COMPLEXITIES = {
    UNIQUE_SPANNING_COLOR_SCALAR: 12,
    MAX_AREA_COMPONENT_COLUMNS: 18,
    ROW_TRANSLATION_RECURRENCE_SQUARE: 20,
}
_OUTPUT_SHAPE_CONTRACTS = {
    UNIQUE_SPANNING_COLOR_SCALAR: "scalar_1x1",
    MAX_AREA_COMPONENT_COLUMNS: (
        "height=max_component_area,width=argmax_component_count"
    ),
    ROW_TRANSLATION_RECURRENCE_SQUARE: "input_width_by_input_width",
}


class AggregateRenderError(ValueError):
    """Base class for invalid aggregate programs and source rasters."""


class AggregateRenderAbstention(AggregateRenderError):
    """Raised when an input has no unique admissible structural rendering."""


class AggregateRenderAmbiguityError(AggregateRenderAbstention):
    """Raised when exact programs or recurrence hypotheses disagree."""


class AggregateRenderLimitError(AggregateRenderError):
    """Raised before a configured finite resource budget is exceeded."""


@dataclass(frozen=True)
class AggregateRenderLimits:
    """Hard representation and enumeration budgets."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_components: int = 128
    maximum_examples: int = 8
    maximum_tests: int = 8
    maximum_programs: int = 3
    maximum_candidates: int = 3
    maximum_recurrence_hypotheses: int = 900

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or int(value) <= 0
            ):
                raise AggregateRenderLimitError(
                    f"{name} must be a positive integer"
                )

    def to_record(self) -> Dict[str, int]:
        return {name: int(value) for name, value in asdict(self).items()}


DEFAULT_LIMITS = AggregateRenderLimits()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def aggregate_render_implementation_fingerprint() -> str:
    """Hash the executable interpreter and compiler source."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class AggregateRenderProgram:
    """One canonical operator with no learned literal payload."""

    operator: str
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise AggregateRenderError(
                f"unsupported schema version {self.schema_version}; "
                f"expected {SCHEMA_VERSION}"
            )
        if self.operator not in _OPERATORS:
            raise AggregateRenderError(
                f"unknown aggregate-render operator {self.operator!r}"
            )

    @classmethod
    def from_record(cls, raw: object) -> "AggregateRenderProgram":
        if not isinstance(raw, Mapping):
            raise AggregateRenderError("aggregate-render program must be a mapping")
        expected = {"schema", "schema_version", "operator"}
        present = set(raw)
        if present != expected:
            raise AggregateRenderError(
                "aggregate-render program fields do not match schema; "
                f"missing={sorted(expected - present)}, "
                f"extra={sorted(present - expected)}"
            )
        if raw["schema"] != SCHEMA:
            raise AggregateRenderError(
                f"unknown aggregate-render schema {raw['schema']!r}"
            )
        return cls(
            operator=str(raw["operator"]),
            schema_version=int(raw["schema_version"]),
        )

    @classmethod
    def unique_spanning_color_scalar(cls) -> "AggregateRenderProgram":
        return cls(UNIQUE_SPANNING_COLOR_SCALAR)

    @classmethod
    def max_area_component_columns(cls) -> "AggregateRenderProgram":
        return cls(MAX_AREA_COMPONENT_COLUMNS)

    @classmethod
    def row_translation_recurrence_square(cls) -> "AggregateRenderProgram":
        return cls(ROW_TRANSLATION_RECURRENCE_SQUARE)

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
        return hashlib.sha256(
            _canonical_json(self.to_record()).encode("ascii")
        ).hexdigest()

    def content_hash(self) -> str:
        return self.program_hash()

    @property
    def complexity(self) -> int:
        return int(_COMPLEXITIES[self.operator])

    def apply(
        self,
        grid: Array,
        *,
        limits: AggregateRenderLimits = DEFAULT_LIMITS,
    ) -> Array:
        return execute_aggregate_render_program(self, grid, limits=limits)


@dataclass(frozen=True)
class _Component:
    color: int
    cells: Tuple[Cell, ...]
    box: Box

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def left(self) -> int:
        return int(self.box[1])


def _validated_grid(grid: Array, limits: AggregateRenderLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise AggregateRenderAbstention("grid must be a nonempty matrix")
    if not np.issubdtype(raw.dtype, np.integer):
        raise AggregateRenderAbstention("grid values must be integers")
    values = np.asarray(raw, dtype=np.int64)
    height, width = values.shape
    if (
        height > limits.maximum_height
        or width > limits.maximum_width
        or values.size > limits.maximum_cells
    ):
        raise AggregateRenderLimitError("grid exceeds ARC representation limits")
    palette = np.unique(values)
    if len(palette) > limits.maximum_palette:
        raise AggregateRenderLimitError("palette exceeds representation limit")
    if np.any(palette < 0) or np.any(palette > 9):
        raise AggregateRenderAbstention("grid colors must lie in the ARC palette")
    return values.copy()


def _background(grid: Array) -> int:
    values, counts = np.unique(grid, return_counts=True)
    maximum = int(counts.max())
    modes = values[counts == maximum]
    if len(modes) != 1:
        raise AggregateRenderAbstention("global background mode is not unique")
    return int(modes[0])


def _components(
    source: Array,
    background: int,
    limits: AggregateRenderLimits,
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
                raise AggregateRenderLimitError(
                    "component count exceeds representation limit"
                )
    if not output:
        raise AggregateRenderAbstention("scene has no foreground components")
    return tuple(output)


def _unique_spanning_color_trace(
    source: Array,
) -> Tuple[Array, Dict[str, object]]:
    background = _background(source)
    candidates = []
    row_spanners = set()
    column_spanners = set()
    for value in np.unique(source):
        color = int(value)
        if color == background:
            continue
        if bool(np.any(np.all(source == color, axis=1))):
            row_spanners.add(color)
        if bool(np.any(np.all(source == color, axis=0))):
            column_spanners.add(color)
        if color in row_spanners or color in column_spanners:
            candidates.append(color)
    if len(candidates) != 1:
        raise AggregateRenderAbstention(
            "foreground spanning color is absent or non-unique"
        )
    selected = int(candidates[0])
    orientation = (
        "both"
        if selected in row_spanners and selected in column_spanners
        else "row"
        if selected in row_spanners
        else "column"
    )
    return (
        np.asarray([[selected]], dtype=np.int64),
        {
            "orientation": orientation,
            "candidate_count": int(len(candidates)),
        },
    )


def _max_area_component_columns_trace(
    source: Array,
    limits: AggregateRenderLimits,
) -> Tuple[Array, Dict[str, object]]:
    background = _background(source)
    components = _components(source, background, limits)
    color_multiplicities: Dict[int, int] = {}
    for component in components:
        color_multiplicities[component.color] = (
            color_multiplicities.get(component.color, 0) + 1
        )
    if any(count != 1 for count in color_multiplicities.values()):
        raise AggregateRenderAbstention(
            "each foreground color must denote exactly one component"
        )
    maximum_area = max(component.area for component in components)
    selected = [
        component
        for component in components
        if component.area == maximum_area
    ]
    left_edges = [component.left for component in selected]
    if len(set(left_edges)) != len(left_edges):
        raise AggregateRenderAbstention(
            "maximum-area components have tied left-edge order"
        )
    selected.sort(key=lambda component: component.left)
    if (
        maximum_area > limits.maximum_height
        or len(selected) > limits.maximum_width
        or maximum_area * len(selected) > limits.maximum_cells
    ):
        raise AggregateRenderLimitError(
            "component serialization exceeds output limits"
        )
    colors = np.asarray(
        [component.color for component in selected],
        dtype=np.int64,
    )
    output = np.tile(colors, (maximum_area, 1))
    return (
        output,
        {
            "maximum_area": int(maximum_area),
            "selected_count": int(len(selected)),
            "component_count": int(len(components)),
            "discarded_count": int(len(components) - len(selected)),
        },
    )


def _shift_row(row: Array, offset: int, background: int) -> Array:
    values = np.asarray(row, dtype=np.int64)
    width = int(values.shape[0])
    output = np.full(values.shape, int(background), dtype=np.int64)
    if offset >= 0:
        if offset < width:
            output[offset:] = values[: width - offset]
    elif -offset < width:
        output[:offset] = values[-offset:]
    return output


def _render_row_recurrence(
    source: Array,
    period: int,
    shift: int,
    background: int,
) -> Array:
    height, width = source.shape
    output = np.full((width, width), int(background), dtype=np.int64)
    output[:height, :] = source
    for row in range(height, width):
        output[row, :] = _shift_row(
            output[row - period, :],
            shift,
            background,
        )
    return output


def _row_translation_recurrence_trace(
    source: Array,
    limits: AggregateRenderLimits,
) -> Tuple[Array, Dict[str, object]]:
    height, width = source.shape
    if height >= width:
        raise AggregateRenderAbstention(
            "row recurrence requires a proper top prefix of a square canvas"
        )
    if width * width > limits.maximum_cells:
        raise AggregateRenderLimitError("square recurrence output exceeds limits")
    background = _background(source)
    hypotheses = []
    for period in range(1, height // 2 + 1):
        for shift in range(-width + 1, width):
            if all(
                np.array_equal(
                    source[row, :],
                    _shift_row(
                        source[row - period, :],
                        shift,
                        background,
                    ),
                )
                for row in range(period, height)
            ):
                hypotheses.append((period, shift))
                if len(hypotheses) > limits.maximum_recurrence_hypotheses:
                    raise AggregateRenderLimitError(
                        "recurrence hypothesis count exceeds limit"
                    )
    if not hypotheses:
        raise AggregateRenderAbstention(
            "no twice-witnessed row translation recurrence"
        )
    behaviors: Dict[bytes, Tuple[Array, list[Tuple[int, int]]]] = {}
    for period, shift in hypotheses:
        prediction = _render_row_recurrence(
            source,
            period,
            shift,
            background,
        )
        key = prediction.tobytes(order="C")
        if key not in behaviors:
            behaviors[key] = (prediction, [])
        behaviors[key][1].append((period, shift))
    if len(behaviors) != 1:
        raise AggregateRenderAmbiguityError(
            "exact row recurrence hypotheses predict divergent continuations"
        )
    output, agreeing = next(iter(behaviors.values()))
    canonical_period, canonical_shift = min(
        agreeing,
        key=lambda item: (item[0], abs(item[1]), item[1]),
    )
    return (
        output,
        {
            "canonical_period": int(canonical_period),
            "canonical_shift": int(canonical_shift),
            "hypothesis_count": int(len(hypotheses)),
            "agreeing_hypothesis_count": int(len(agreeing)),
        },
    )


def _execute_with_trace(
    program: AggregateRenderProgram,
    grid: Array,
    limits: AggregateRenderLimits,
) -> Tuple[Array, Dict[str, object]]:
    source = _validated_grid(grid, limits)
    if program.operator == UNIQUE_SPANNING_COLOR_SCALAR:
        output, trace = _unique_spanning_color_trace(source)
    elif program.operator == MAX_AREA_COMPONENT_COLUMNS:
        output, trace = _max_area_component_columns_trace(source, limits)
    elif program.operator == ROW_TRANSLATION_RECURRENCE_SQUARE:
        output, trace = _row_translation_recurrence_trace(source, limits)
    else:
        raise AggregateRenderError(
            f"unknown aggregate-render operator {program.operator!r}"
        )
    return _validated_grid(output, limits), trace


def execute_aggregate_render_program(
    program: AggregateRenderProgram | Mapping[str, object],
    grid: Array,
    *,
    limits: AggregateRenderLimits = DEFAULT_LIMITS,
) -> Array:
    """Rebind and execute one aggregate-render program."""

    if not isinstance(program, AggregateRenderProgram):
        program = AggregateRenderProgram.from_record(program)
    output, _ = _execute_with_trace(program, grid, limits)
    return output.copy()


@dataclass(frozen=True)
class AggregateRenderCandidate:
    """Entry-independent exact candidate with a canonical executable record."""

    name: str
    program: AggregateRenderProgram
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


def _enumerate_programs(
    limits: AggregateRenderLimits,
) -> Tuple[AggregateRenderProgram, ...]:
    programs = tuple(
        sorted(
            (AggregateRenderProgram(operator) for operator in _OPERATORS),
            key=lambda program: (program.complexity, program.semantic_key),
        )
    )
    if len(programs) > limits.maximum_programs:
        raise AggregateRenderLimitError(
            f"program grammar has {len(programs)} entries; "
            f"limit is {limits.maximum_programs}"
        )
    return programs


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


def _validated_train(
    train: Sequence[Tuple[Array, Array]],
    limits: AggregateRenderLimits,
) -> Tuple[Tuple[Array, Array], ...]:
    return tuple(
        (
            _validated_grid(source, limits),
            _validated_grid(target, limits),
        )
        for source, target in train
    )


def _exact_program_predictions(
    train: Sequence[Tuple[Array, Array]],
    programs: Sequence[AggregateRenderProgram],
    limits: AggregateRenderLimits,
) -> Dict[str, Tuple[AggregateRenderProgram, Tuple[Array, ...]]]:
    exact: Dict[
        str,
        Tuple[AggregateRenderProgram, Tuple[Array, ...]],
    ] = {}
    for program in programs:
        predictions = []
        try:
            for source, target in train:
                prediction = program.apply(source, limits=limits)
                if not np.array_equal(prediction, target):
                    break
                predictions.append(prediction)
            else:
                exact[program.program_hash()] = (
                    program,
                    tuple(predictions),
                )
        except AggregateRenderError:
            continue
    return exact


def _discover_exact_program(
    train: Sequence[Tuple[Array, Array]],
    programs: Sequence[AggregateRenderProgram],
    limits: AggregateRenderLimits,
) -> Optional[Tuple[AggregateRenderProgram, Tuple[Array, ...]]]:
    exact = _exact_program_predictions(train, programs, limits)
    if not exact:
        return None
    return min(
        exact.values(),
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )


def _support_record(
    program: AggregateRenderProgram,
    train: Sequence[Tuple[Array, Array]],
    limits: AggregateRenderLimits,
) -> Optional[Dict[str, object]]:
    traces = []
    try:
        for source, _ in train:
            _, trace = _execute_with_trace(program, source, limits)
            traces.append(trace)
    except AggregateRenderError:
        return None
    if program.operator == UNIQUE_SPANNING_COLOR_SCALAR:
        orientations = {str(trace["orientation"]) for trace in traces}
        selected_values = {
            int(program.apply(source, limits=limits)[0, 0])
            for source, _ in train
        }
        row_supported = bool(orientations & {"row", "both"})
        column_supported = bool(orientations & {"column", "both"})
        if (
            len(selected_values) < 2
            or not row_supported
            or not column_supported
        ):
            return None
        return {
            "selected_value_variation": int(len(selected_values)),
            "row_span_witnessed": row_supported,
            "column_span_witnessed": column_supported,
        }
    if program.operator == MAX_AREA_COMPONENT_COLUMNS:
        maximum_areas = {int(trace["maximum_area"]) for trace in traces}
        selected_counts = {int(trace["selected_count"]) for trace in traces}
        unique_winner = any(int(trace["selected_count"]) == 1 for trace in traces)
        tied_winner = any(int(trace["selected_count"]) > 1 for trace in traces)
        distractor = any(int(trace["discarded_count"]) > 0 for trace in traces)
        if (
            len(maximum_areas) < 2
            or len(selected_counts) < 2
            or not unique_winner
            or not tied_winner
            or not distractor
        ):
            return None
        return {
            "maximum_area_variation": int(len(maximum_areas)),
            "argmax_cardinality_variation": int(len(selected_counts)),
            "unique_winner_witnessed": unique_winner,
            "tied_winner_witnessed": tied_winner,
            "discarded_distractor_witnessed": distractor,
        }
    if program.operator == ROW_TRANSLATION_RECURRENCE_SQUARE:
        periods = {int(trace["canonical_period"]) for trace in traces}
        shifts = {int(trace["canonical_shift"]) for trace in traces}
        if (
            len(periods) < 2
            or not any(period > 1 for period in periods)
            or not any(shift != 0 for shift in shifts)
        ):
            return None
        return {
            "period_variation": int(len(periods)),
            "shift_variation": int(len(shifts)),
            "nonzero_shift_witnessed": True,
            "multirow_period_witnessed": True,
        }
    return None


def compile_aggregate_render_programs(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: AggregateRenderLimits = DEFAULT_LIMITS,
) -> Tuple[AggregateRenderCandidate, ...]:
    """Compile exact, LOO-stable programs from training rasters only."""

    if len(train) < 2:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise AggregateRenderLimitError("example budget exceeded")
    try:
        validated = _validated_train(train, limits)
        validated_tests = tuple(
            _validated_grid(test, limits)
            for test in tests
        )
    except AggregateRenderAbstention:
        return ()

    groups: Dict[str, list[int]] = {}
    for index, (source, target) in enumerate(validated):
        if np.array_equal(source, target):
            continue
        groups.setdefault(_example_hash(source, target), []).append(index)
    if len(groups) < 2:
        return ()

    programs = _enumerate_programs(limits)
    full_exact = _exact_program_predictions(validated, programs, limits)
    if not full_exact:
        return ()
    discovered = min(
        full_exact.values(),
        key=lambda item: (item[0].complexity, item[0].semantic_key),
    )
    program, train_predictions = discovered
    program_hash = program.program_hash()
    support = _support_record(program, validated, limits)
    if support is None:
        return ()

    exact_test_behaviors: Dict[str, list[str]] = {}
    selected_test_predictions: Optional[Tuple[Array, ...]] = None
    for exact_hash, (exact_program, _) in sorted(full_exact.items()):
        try:
            predictions = tuple(
                exact_program.apply(test, limits=limits)
                for test in validated_tests
            )
        except AggregateRenderError:
            return ()
        behavior = _behavior_hash(predictions)
        exact_test_behaviors.setdefault(behavior, []).append(exact_hash)
        if exact_hash == program_hash:
            selected_test_predictions = predictions
    if len(exact_test_behaviors) > limits.maximum_candidates:
        raise AggregateRenderLimitError(
            "exact test behavior-class budget exceeded"
        )
    if len(exact_test_behaviors) != 1:
        raise AggregateRenderAmbiguityError(
            "full-data-exact aggregate programs predict divergent tests"
        )
    if selected_test_predictions is None:
        return ()

    loo_program_hashes = []
    loo_exact = 0
    for indices in groups.values():
        excluded = set(indices)
        construction = tuple(
            pair
            for index, pair in enumerate(validated)
            if index not in excluded
        )
        rediscovered = _discover_exact_program(
            construction,
            programs,
            limits,
        )
        if rediscovered is None:
            break
        fold_program = rediscovered[0]
        fold_hash = fold_program.program_hash()
        loo_program_hashes.append(fold_hash)
        if fold_hash != program_hash:
            break
        try:
            if not all(
                np.array_equal(
                    fold_program.apply(
                        validated[index][0],
                        limits=limits,
                    ),
                    validated[index][1],
                )
                for index in indices
            ):
                break
        except AggregateRenderError:
            break
        loo_exact += 1
    if loo_exact != len(groups):
        return ()

    d4_equivariant = program.operator == UNIQUE_SPANNING_COLOR_SCALAR
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.aggregate-render-candidate.v1",
        "program": program.to_record(),
        "program_hash": program_hash,
        "semantic_key": program.semantic_key,
        "operator": program.operator,
        "background_binding": "unique_global_mode",
        "output_shape_contract": _OUTPUT_SHAPE_CONTRACTS[program.operator],
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "test_input_grounded": True,
        "task_identifier_free": True,
        "literal_color_free_program": True,
        "literal_coordinate_free_program": True,
        "raw_grid_free_program": True,
        "palette_equivariant": True,
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
        "loo_program_hashes": list(loo_program_hashes),
        "full_exact_program_count": int(len(full_exact)),
        "exact_test_behavior_count": int(len(exact_test_behaviors)),
        "support": support,
        "empirical_promotion_eligible": False,
        "external_gain_loss_audit": False,
        "implementation_fingerprint": (
            aggregate_render_implementation_fingerprint()
        ),
        "bounded_program_count": int(len(programs)),
        "limits": limits.to_record(),
    }
    return (
        AggregateRenderCandidate(
            name=f"aggregate_render:{program.operator}:{program_hash[:12]}",
            program=program,
            grids=selected_test_predictions,
            train_grids=train_predictions,
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


aggregate_render_candidates = compile_aggregate_render_programs


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "MAX_AREA_COMPONENT_COLUMNS",
    "ROW_TRANSLATION_RECURRENCE_SQUARE",
    "UNIQUE_SPANNING_COLOR_SCALAR",
    "AggregateRenderAbstention",
    "AggregateRenderAmbiguityError",
    "AggregateRenderCandidate",
    "AggregateRenderError",
    "AggregateRenderLimitError",
    "AggregateRenderLimits",
    "AggregateRenderProgram",
    "aggregate_render_candidates",
    "aggregate_render_implementation_fingerprint",
    "compile_aggregate_render_programs",
    "execute_aggregate_render_program",
]
