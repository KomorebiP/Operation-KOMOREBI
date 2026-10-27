"""Finite, task-agnostic synthesis of dynamic scene-layout programs.

The Block 6 mosaic compiler stores a literal block pattern.  That is the
right representation when the layout is constant across demonstrations, but
it cannot express layouts whose dimensions or occupied blocks are derived
from the current input.  This module provides that missing higher-order leaf:
the input scene supplies both a layout and a payload packet.

Only labelled training demonstrations are inspected by the compiler.  Test
examples are deliberately outside the compilation path; :func:`predict`
reads their ``input`` member and ignores every other member.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from numbers import Integral
from typing import Any, Iterable, Mapping, Sequence


Grid = tuple[tuple[int, ...], ...]

SCHEMA = "komorebi.lasm_dynamic_layout"
SCHEMA_VERSION = 1
FAMILY = "dynamic_layout_from_scene"
MACRO_SCHEMA = "layout_from_scene"
MAX_PROPOSALS = 4096

_LAYOUT_MODES = frozenset({
    "selector_mask",
    "all_cells",
    "color_equality_kernel",
    "fixed_d4_pattern",
    "dynamic_pair_repeat",
})
_SELECTOR_MODES = frozenset({
    "none",
    "fixed_color",
    "frequency_rank",
    "unique_axis_line_color",
})
_FREQUENCY_ORDERS = frozenset({"ascending", "descending"})
_D4 = (
    "id",
    "r90",
    "r180",
    "r270",
    "fliplr",
    "flipud",
    "transpose",
    "anti_transpose",
)
_PAIR_AXES = frozenset({"horizontal", "vertical"})
_REPEAT_AXES = frozenset({"rows", "columns"})
_REPEAT_COUNTS = frozenset({"source_height", "source_width"})


def validate_grid(value: Any, *, output: bool = False) -> Grid:
    """Return an immutable ARC grid or raise ``ValueError``.

    ARC grids are nonempty rectangular arrays with categorical values 0--9.
    Generated outputs additionally respect the standard 30 by 30 boundary.
    The explicit check keeps this leaf safe when it is called outside the
    surrounding Block 9 model layer.
    """

    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError("a grid must be a nonempty sequence of rows")
    if len(value) > 30:
        raise ValueError("grid height must not exceed 30")
    rows: list[tuple[int, ...]] = []
    width: int | None = None
    for raw_row in value:
        if isinstance(raw_row, (str, bytes)) or not isinstance(raw_row, Sequence) or not raw_row:
            raise ValueError("every grid row must be a nonempty sequence")
        if len(raw_row) > 30:
            raise ValueError("grid width must not exceed 30")
        row: list[int] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, bool) or not isinstance(raw_cell, Integral):
                raise ValueError("grid cells must be integer categories")
            cell = int(raw_cell)
            if not 0 <= cell <= 9:
                raise ValueError("grid cells must lie in the categorical range 0..9")
            row.append(cell)
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("a grid must be rectangular")
        rows.append(tuple(row))
    grid = tuple(rows)
    if len(grid) > 30 or (width or 0) > 30:
        kind = "generated output" if output else "input"
        raise ValueError(f"{kind} exceeds the 30 by 30 ARC grid boundary")
    return grid


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


@dataclass(frozen=True)
class DynamicLayoutParameters:
    """A closed, finite parameter record for one dynamic-layout program."""

    layout_mode: str
    blank_color: int
    selector_mode: str = "none"
    selector_color: int | None = None
    selector_rank: int | None = None
    frequency_order: str | None = None
    payload_transform: str = "id"
    pair_left_transform: str | None = None
    pair_right_transform: str | None = None
    pair_axis: str | None = None
    repeat_axis: str | None = None
    repeat_count: str | None = None
    d4_pattern: tuple[tuple[str, ...], ...] | None = None

    def __post_init__(self) -> None:
        if self.layout_mode not in _LAYOUT_MODES:
            raise ValueError(f"unknown dynamic layout mode {self.layout_mode!r}")
        if isinstance(self.blank_color, bool) or not isinstance(self.blank_color, Integral):
            raise ValueError("blank_color must be an integer category")
        if not 0 <= int(self.blank_color) <= 9:
            raise ValueError("blank_color must lie in 0..9")
        object.__setattr__(self, "blank_color", int(self.blank_color))
        if self.selector_mode not in _SELECTOR_MODES:
            raise ValueError(f"unknown selector mode {self.selector_mode!r}")
        if self.payload_transform not in _D4:
            raise ValueError(f"unknown payload transform {self.payload_transform!r}")

        needs_selector = self.layout_mode == "selector_mask"
        if needs_selector != (self.selector_mode != "none"):
            raise ValueError("only selector-mask layouts may carry a selector")
        if self.selector_mode == "fixed_color":
            if (
                isinstance(self.selector_color, bool)
                or not isinstance(self.selector_color, Integral)
                or not 0 <= int(self.selector_color) <= 9
            ):
                raise ValueError("fixed-color selectors require a color in 0..9")
            object.__setattr__(self, "selector_color", int(self.selector_color))
        elif self.selector_color is not None:
            raise ValueError("selector_color is valid only for fixed-color selectors")
        if self.selector_mode == "frequency_rank":
            if (
                isinstance(self.selector_rank, bool)
                or not isinstance(self.selector_rank, Integral)
                or self.selector_rank < 0
            ):
                raise ValueError("frequency-rank selectors require a nonnegative rank")
            object.__setattr__(self, "selector_rank", int(self.selector_rank))
            if self.frequency_order not in _FREQUENCY_ORDERS:
                raise ValueError("frequency-rank selectors require an ordering")
        elif self.selector_rank is not None or self.frequency_order is not None:
            raise ValueError("rank and frequency_order are valid only for frequency-rank selectors")

        pair_fields = (
            self.pair_left_transform,
            self.pair_right_transform,
            self.pair_axis,
            self.repeat_axis,
            self.repeat_count,
        )
        if self.layout_mode == "fixed_d4_pattern":
            if (
                isinstance(self.d4_pattern, (str, bytes))
                or not isinstance(self.d4_pattern, Sequence)
                or not self.d4_pattern
            ):
                raise ValueError("fixed D4 layouts require a nonempty transform pattern")
            normalized_rows: list[tuple[str, ...]] = []
            for row in self.d4_pattern:
                if isinstance(row, (str, bytes)) or not isinstance(row, Sequence) or not row:
                    raise ValueError("fixed D4 layouts require nonempty pattern rows")
                if any(not isinstance(name, str) for name in row):
                    raise ValueError("D4 transform names must be strings")
                normalized_rows.append(tuple(row))
            normalized_pattern = tuple(normalized_rows)
            width = len(normalized_pattern[0])
            if any(len(row) != width for row in normalized_pattern):
                raise ValueError("a fixed D4 transform pattern must be rectangular")
            if any(name not in _D4 for row in normalized_pattern for name in row):
                raise ValueError("a fixed D4 transform pattern contains an unknown transform")
            if self.payload_transform != "id":
                raise ValueError("fixed D4 layouts encode transforms in their pattern")
            object.__setattr__(self, "d4_pattern", normalized_pattern)
        elif self.d4_pattern is not None:
            raise ValueError("d4_pattern is valid only for fixed D4 layouts")
        if self.layout_mode == "dynamic_pair_repeat":
            if self.pair_left_transform not in _D4 or self.pair_right_transform not in _D4:
                raise ValueError("dynamic pair layouts require two D4 transforms")
            if self.pair_axis not in _PAIR_AXES:
                raise ValueError("dynamic pair layouts require a concatenation axis")
            if self.repeat_axis not in _REPEAT_AXES:
                raise ValueError("dynamic pair layouts require a repetition axis")
            if self.repeat_count not in _REPEAT_COUNTS:
                raise ValueError("dynamic pair layouts require a source-dimension repeat count")
            if self.payload_transform != "id":
                raise ValueError("dynamic pair layouts encode transforms in their pair fields")
        elif any(value is not None for value in pair_fields):
            raise ValueError("pair fields are valid only for dynamic-pair layouts")

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "layout_mode": self.layout_mode,
            "blank_color": int(self.blank_color),
            "selector_mode": self.selector_mode,
            "payload_transform": self.payload_transform,
        }
        optional = {
            "selector_color": self.selector_color,
            "selector_rank": self.selector_rank,
            "frequency_order": self.frequency_order,
            "pair_left_transform": self.pair_left_transform,
            "pair_right_transform": self.pair_right_transform,
            "pair_axis": self.pair_axis,
            "repeat_axis": self.repeat_axis,
            "repeat_count": self.repeat_count,
            "d4_pattern": [list(row) for row in self.d4_pattern] if self.d4_pattern is not None else None,
        }
        record.update({key: value for key, value in optional.items() if value is not None})
        return record

    @classmethod
    def from_record(cls, value: Mapping[str, Any]) -> "DynamicLayoutParameters":
        allowed = {
            "layout_mode", "blank_color", "selector_mode", "selector_color",
            "selector_rank", "frequency_order", "payload_transform",
            "pair_left_transform", "pair_right_transform", "pair_axis",
            "repeat_axis", "repeat_count",
            "d4_pattern",
        }
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown dynamic-layout parameter fields: {sorted(unknown)}")
        try:
            fields = dict(value)
            if fields.get("d4_pattern") is not None:
                pattern = fields["d4_pattern"]
                if isinstance(pattern, (str, bytes)) or not isinstance(pattern, Sequence):
                    raise ValueError("d4_pattern must be a sequence of rows")
                fields["d4_pattern"] = tuple(tuple(name for name in row) for row in pattern)
            return cls(**fields)
        except TypeError as error:
            raise ValueError(f"invalid dynamic-layout parameter record: {error}") from error


@dataclass(frozen=True)
class DynamicLayoutProgram:
    """Canonical executable program emitted after exact demo replay."""

    parameters: DynamicLayoutParameters
    cost: int
    family: str = FAMILY
    macro_schema: str = MACRO_SCHEMA
    schema: str = SCHEMA
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, DynamicLayoutParameters):
            raise ValueError("program parameters must be DynamicLayoutParameters")
        if self.family != FAMILY or self.macro_schema != MACRO_SCHEMA:
            raise ValueError("dynamic-layout program family/schema mismatch")
        if (
            self.schema != SCHEMA
            or isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, Integral)
            or int(self.schema_version) != SCHEMA_VERSION
        ):
            raise ValueError("unsupported dynamic-layout program schema version")
        if isinstance(self.cost, bool) or not isinstance(self.cost, Integral) or self.cost < 1:
            raise ValueError("program cost must be a positive integer")
        object.__setattr__(self, "schema_version", int(self.schema_version))
        object.__setattr__(self, "cost", int(self.cost))

    @property
    def signature_record(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "macro_schema": self.macro_schema,
            "parameters": self.parameters.to_record(),
        }

    @property
    def signature_hash(self) -> str:
        return hashlib.sha256(_canonical_json(self.signature_record).encode("utf-8")).hexdigest()

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            **self.signature_record,
            "cost": int(self.cost),
            "signature_hash": self.signature_hash,
            "description": "Derive a dynamic layout and payload packet from the current scene.",
        }


def _rotate90(grid: Grid) -> Grid:
    return tuple(tuple(grid[len(grid) - 1 - y][x] for y in range(len(grid))) for x in range(len(grid[0])))


def _transform(grid: Grid, name: str) -> Grid:
    if name == "id":
        return grid
    if name == "r90":
        return _rotate90(grid)
    if name == "r180":
        return _rotate90(_rotate90(grid))
    if name == "r270":
        return _rotate90(_rotate90(_rotate90(grid)))
    if name == "fliplr":
        return tuple(tuple(reversed(row)) for row in grid)
    if name == "flipud":
        return tuple(reversed(grid))
    if name == "transpose":
        return tuple(tuple(grid[y][x] for y in range(len(grid))) for x in range(len(grid[0])))
    if name == "anti_transpose":
        return _transform(_transform(_transform(grid, "transpose"), "fliplr"), "flipud")
    raise ValueError(f"unknown D4 transform {name!r}")


def _color_counts(grid: Grid) -> dict[int, int]:
    counts: dict[int, int] = {}
    for row in grid:
        for color in row:
            counts[color] = counts.get(color, 0) + 1
    return counts


def _selected_color(grid: Grid, parameters: DynamicLayoutParameters) -> int:
    if parameters.selector_mode == "fixed_color":
        assert parameters.selector_color is not None
        return int(parameters.selector_color)
    counts = _color_counts(grid)
    if parameters.selector_mode == "frequency_rank":
        assert parameters.selector_rank is not None and parameters.frequency_order is not None
        reverse = parameters.frequency_order == "descending"
        ordered = sorted(counts, key=lambda color: ((-counts[color], color) if reverse else (counts[color], color)))
        rank = int(parameters.selector_rank)
        if rank >= len(ordered):
            raise ValueError("selector frequency rank is unavailable in this scene")
        return ordered[rank]
    if parameters.selector_mode == "unique_axis_line_color":
        height, width = len(grid), len(grid[0])
        candidates: list[int] = []
        for color in sorted(counts):
            cells = [(y, x) for y, row in enumerate(grid) for x, value in enumerate(row) if value == color]
            rows = {y for y, _ in cells}
            columns = {x for _, x in cells}
            is_full_row = len(rows) == 1 and len(cells) == width
            is_full_column = len(columns) == 1 and len(cells) == height
            if is_full_row or is_full_column:
                candidates.append(color)
        if len(candidates) != 1:
            raise ValueError("axis-line selector is not unique in this scene")
        return candidates[0]
    raise ValueError("the selected layout mode has no color selector")


def _blank(height: int, width: int, color: int) -> Grid:
    return tuple(tuple(color for _ in range(width)) for _ in range(height))


def _hstack(grids: Sequence[Grid]) -> Grid:
    if not grids or len({len(grid) for grid in grids}) != 1:
        raise ValueError("horizontal packing requires equal nonempty heights")
    return tuple(tuple(cell for grid in grids for cell in grid[y]) for y in range(len(grids[0])))


def _vstack(grids: Sequence[Grid]) -> Grid:
    if not grids or len({len(grid[0]) for grid in grids}) != 1:
        raise ValueError("vertical packing requires equal nonempty widths")
    return tuple(row for grid in grids for row in grid)


def _pack(block_rows: Sequence[Sequence[Grid]]) -> Grid:
    if not block_rows or any(not row for row in block_rows):
        raise ValueError("a dynamic layout must contain at least one block")
    packed_rows = tuple(_hstack(tuple(row)) for row in block_rows)
    return _vstack(packed_rows)


def execute_dynamic_layout(
    grid: Any,
    parameters: DynamicLayoutParameters | DynamicLayoutProgram | Mapping[str, Any],
) -> Grid:
    """Execute one validated dynamic-layout program on one input grid."""

    source = validate_grid(grid)
    if isinstance(parameters, DynamicLayoutProgram):
        params = parameters.parameters
    elif isinstance(parameters, DynamicLayoutParameters):
        params = parameters
    else:
        record = parameters.get("parameters", parameters)
        if not isinstance(record, Mapping):
            raise ValueError("dynamic-layout parameters must be a mapping")
        params = DynamicLayoutParameters.from_record(record)

    height, width = len(source), len(source[0])
    blank_color = int(params.blank_color)
    if params.layout_mode == "fixed_d4_pattern":
        assert params.d4_pattern is not None
        result = _pack(tuple(tuple(_transform(source, name) for name in row) for row in params.d4_pattern))
        return validate_grid(result, output=True)
    if params.layout_mode == "dynamic_pair_repeat":
        assert params.pair_left_transform is not None and params.pair_right_transform is not None
        assert params.pair_axis is not None and params.repeat_axis is not None and params.repeat_count is not None
        left = _transform(source, params.pair_left_transform)
        right = _transform(source, params.pair_right_transform)
        pair = _hstack((left, right)) if params.pair_axis == "horizontal" else _vstack((left, right))
        count = height if params.repeat_count == "source_height" else width
        result = _vstack(tuple(pair for _ in range(count))) if params.repeat_axis == "rows" else _hstack(tuple(pair for _ in range(count)))
        return validate_grid(result, output=True)

    payload = _transform(source, params.payload_transform)
    payload_height, payload_width = len(payload), len(payload[0])
    blank_payload = _blank(payload_height, payload_width, blank_color)
    blocks: list[list[Grid]] = []
    selected = _selected_color(source, params) if params.layout_mode == "selector_mask" else None
    for layout_y, row in enumerate(source):
        block_row: list[Grid] = []
        for layout_x, cell in enumerate(row):
            if params.layout_mode == "all_cells":
                block = payload
            elif params.layout_mode == "selector_mask":
                block = payload if cell == selected else blank_payload
            elif params.layout_mode == "color_equality_kernel":
                masked = tuple(
                    tuple(value if value == cell else blank_color for value in payload_row)
                    for payload_row in source
                )
                block = _transform(masked, params.payload_transform)
            else:
                raise ValueError(f"unsupported dynamic layout mode {params.layout_mode!r}")
            block_row.append(block)
        blocks.append(block_row)
    return validate_grid(_pack(blocks), output=True)


def _training_examples(task: Mapping[str, Any]) -> tuple[tuple[Grid, Grid], ...]:
    raw = task.get("train")
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence) or not raw:
        raise ValueError("dynamic-layout compilation requires labelled training demonstrations")
    examples: list[tuple[Grid, Grid]] = []
    for example in raw:
        if not isinstance(example, Mapping) or "input" not in example or "output" not in example:
            raise ValueError("every training demonstration needs input and output grids")
        examples.append((validate_grid(example["input"]), validate_grid(example["output"], output=True)))
    return tuple(examples)


def _candidate_parameters(examples: Sequence[tuple[Grid, Grid]]) -> Iterable[DynamicLayoutParameters]:
    input_colors = sorted({cell for source, _ in examples for row in source for cell in row})
    output_colors = sorted({cell for _, target in examples for row in target for cell in row})
    blank_colors = tuple(sorted(set(output_colors) | {0}))

    selectors: list[tuple[str, int | None, int | None, str | None]] = []
    selectors.extend(("fixed_color", color, None, None) for color in input_colors)
    maximum_palette = max(len(_color_counts(source)) for source, _ in examples)
    for rank in range(maximum_palette):
        selectors.append(("frequency_rank", None, rank, "ascending"))
        selectors.append(("frequency_rank", None, rank, "descending"))
    selectors.append(("unique_axis_line_color", None, None, None))

    def transformed_shape(source: Grid, transform: str) -> tuple[int, int]:
        height, width = len(source), len(source[0])
        return (width, height) if transform in {"r90", "r270", "transpose", "anti_transpose"} else (height, width)

    viable_payload_transforms = []
    for transform in _D4:
        if all(
            (len(target), len(target[0]))
            == (len(source) * transformed_shape(source, transform)[0],
                len(source[0]) * transformed_shape(source, transform)[1])
            for source, target in examples
        ):
            viable_payload_transforms.append(transform)

    for transform in viable_payload_transforms:
        # blank_color is observationally irrelevant when every layout cell is
        # occupied, so keep one canonical encoding for semantic identity.
        yield DynamicLayoutParameters(
            layout_mode="all_cells",
            blank_color=0,
            payload_transform=transform,
        )

    for blank_color in blank_colors:
        for transform in viable_payload_transforms:
            yield DynamicLayoutParameters(
                layout_mode="color_equality_kernel",
                blank_color=blank_color,
                payload_transform=transform,
            )
            for selector_mode, selector_color, selector_rank, order in selectors:
                yield DynamicLayoutParameters(
                    layout_mode="selector_mask",
                    blank_color=blank_color,
                    selector_mode=selector_mode,
                    selector_color=selector_color,
                    selector_rank=selector_rank,
                    frequency_order=order,
                    payload_transform=transform,
                )

    # A finite dynamic packing sublanguage.  Shape checks in exact replay make
    # this inexpensive in practice, while retaining rectangular-input cases.
    for left in _D4:
        for right in _D4:
            for pair_axis in sorted(_PAIR_AXES):
                for repeat_axis in sorted(_REPEAT_AXES):
                    for repeat_count in sorted(_REPEAT_COUNTS):
                        viable = True
                        for source, target in examples:
                            left_shape = transformed_shape(source, left)
                            right_shape = transformed_shape(source, right)
                            if pair_axis == "horizontal":
                                if left_shape[0] != right_shape[0]:
                                    viable = False
                                    break
                                pair_shape = (left_shape[0], left_shape[1] + right_shape[1])
                            else:
                                if left_shape[1] != right_shape[1]:
                                    viable = False
                                    break
                                pair_shape = (left_shape[0] + right_shape[0], left_shape[1])
                            count = len(source) if repeat_count == "source_height" else len(source[0])
                            result_shape = (
                                (pair_shape[0] * count, pair_shape[1])
                                if repeat_axis == "rows"
                                else (pair_shape[0], pair_shape[1] * count)
                            )
                            if result_shape != (len(target), len(target[0])):
                                viable = False
                                break
                        if not viable:
                            continue
                        yield DynamicLayoutParameters(
                            layout_mode="dynamic_pair_repeat",
                            blank_color=0,
                            pair_left_transform=left,
                            pair_right_transform=right,
                            pair_axis=pair_axis,
                            repeat_axis=repeat_axis,
                            repeat_count=repeat_count,
                        )

    # Resolve a fixed D4 block pattern jointly across all demonstrations.
    # Looking only at the first example is incomplete when a symmetric packet
    # makes several transforms observationally equal.  Intersecting the
    # per-block transform sets across every example supplies the conservative
    # cross-demonstration choice used here.
    pattern_shape: tuple[int, int] | None = None
    choices: list[list[set[str]]] | None = None
    for source, target in examples:
        source_height, source_width = len(source), len(source[0])
        target_height, target_width = len(target), len(target[0])
        if target_height % source_height or target_width % source_width:
            choices = None
            break
        rows, columns = target_height // source_height, target_width // source_width
        if rows * columns < 2 or rows > 6 or columns > 6:
            choices = None
            break
        if pattern_shape is None:
            pattern_shape = (rows, columns)
            choices = [[set(_D4) for _ in range(columns)] for _ in range(rows)]
        elif pattern_shape != (rows, columns):
            choices = None
            break
        assert choices is not None
        transformed = {name: _transform(source, name) for name in _D4}
        for row in range(rows):
            for column in range(columns):
                block = tuple(
                    tuple(target[y][x] for x in range(column * source_width, (column + 1) * source_width))
                    for y in range(row * source_height, (row + 1) * source_height)
                )
                matches = {name for name, value in transformed.items() if value == block}
                choices[row][column].intersection_update(matches)
    if choices is not None and all(cell for row in choices for cell in row):
        pattern = tuple(tuple(min(cell, key=_D4.index) for cell in row) for row in choices)
        yield DynamicLayoutParameters(
            layout_mode="fixed_d4_pattern",
            blank_color=0,
            d4_pattern=pattern,
        )


def _cost(parameters: DynamicLayoutParameters) -> int:
    if parameters.layout_mode == "all_cells":
        return 5
    if parameters.layout_mode == "selector_mask":
        return 7
    if parameters.layout_mode == "color_equality_kernel":
        return 8
    return 8


def compile_dynamic_layout_with_trace(
    task: Mapping[str, Any],
    *,
    proposal_budget: int = MAX_PROPOSALS,
) -> tuple[tuple[DynamicLayoutProgram, ...], dict[str, Any]]:
    """Compile every finite candidate that exactly replays all demonstrations.

    Candidate generation is task-ID-free and deterministic.  It uses only
    ``task['train'][*]['input'/'output']``; neither attached test outputs nor a
    test input can affect which programs are accepted.
    """

    if (
        isinstance(proposal_budget, bool)
        or not isinstance(proposal_budget, Integral)
        or not 1 <= int(proposal_budget) <= MAX_PROPOSALS
    ):
        raise ValueError(f"proposal_budget must lie in 1..{MAX_PROPOSALS}")
    examples = _training_examples(task)
    accepted: dict[str, DynamicLayoutProgram] = {}
    proposals_considered = 0
    budget_exhausted = False
    for parameters in _candidate_parameters(examples):
        if proposals_considered >= int(proposal_budget):
            budget_exhausted = True
            break
        proposals_considered += 1
        try:
            if not all(execute_dynamic_layout(source, parameters) == target for source, target in examples):
                continue
        except (AssertionError, TypeError, ValueError):
            continue
        program = DynamicLayoutProgram(parameters=parameters, cost=_cost(parameters))
        accepted.setdefault(program.signature_hash, program)
    programs = tuple(sorted(accepted.values(), key=lambda program: (program.cost, program.signature_hash)))
    trace = {
        "schema": "komorebi.lasm_dynamic_layout_compilation_trace",
        "schema_version": 1,
        "proposal_budget": int(proposal_budget),
        "hard_proposal_limit": MAX_PROPOSALS,
        "proposals_considered": proposals_considered,
        "budget_exhausted": budget_exhausted,
        "exact_training_programs": len(programs),
    }
    return programs, trace


def compile_dynamic_layout(
    task: Mapping[str, Any],
    *,
    proposal_budget: int = MAX_PROPOSALS,
) -> tuple[DynamicLayoutProgram, ...]:
    return compile_dynamic_layout_with_trace(task, proposal_budget=proposal_budget)[0]


def predict(task: Mapping[str, Any], program: DynamicLayoutProgram | DynamicLayoutParameters | Mapping[str, Any]) -> tuple[Grid, ...]:
    """Execute a compiled program on sanitized test inputs only."""

    raw = task.get("test", ())
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
        raise ValueError("task test examples must be a sequence")
    outputs: list[Grid] = []
    for example in raw:
        if not isinstance(example, Mapping) or "input" not in example:
            raise ValueError("every test example needs an input grid")
        outputs.append(execute_dynamic_layout(example["input"], program))
    return tuple(outputs)


# Explicit aliases make the leaf easy to register without imposing naming on
# the surrounding composition engine.
compile_programs = compile_dynamic_layout
execute = execute_dynamic_layout


__all__ = [
    "DynamicLayoutParameters",
    "DynamicLayoutProgram",
    "FAMILY",
    "Grid",
    "MACRO_SCHEMA",
    "MAX_PROPOSALS",
    "SCHEMA",
    "SCHEMA_VERSION",
    "compile_dynamic_layout",
    "compile_dynamic_layout_with_trace",
    "compile_programs",
    "execute",
    "execute_dynamic_layout",
    "predict",
    "validate_grid",
]
