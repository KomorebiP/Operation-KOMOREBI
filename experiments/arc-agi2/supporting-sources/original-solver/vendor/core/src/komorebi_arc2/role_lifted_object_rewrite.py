"""A protected role-lifted rewrite for separated payload workspaces.

The v1.4 object-stencil learner keys residual effects by literal component
shape, size, or color.  That is useful for local translation, but it cannot
transfer when a held-out payload introduces a new component key.  This module
implements one deliberately narrow alternative whose reusable program stores
only structural roles.

The admitted scene has three parts along one axis:

* a completely filled, multicolor payload half
* a full monochrome separator through the middle
* an equally deep blank workspace half

The payload must have one strictly modal color.  At execution time that color
is bound to ``DOMINANT_PAYLOAD_COLOR`` and written to the unique outer-center
cell of the blank workspace.  No color, coordinate, task identifier, or test
target is retained by the program.  Horizontal and vertical scenes, either
workspace direction, are handled by the same D4-equivariant role predicate.

The compiler is intentionally independent of ``entry.py``.  It returns a
small candidate record that a thin portfolio adapter can convert to the
legacy ``RuleCandidate`` type without creating an import cycle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Dict, Mapping, Sequence, Tuple

import numpy as np


Array = np.ndarray

ROLE_LIFTED_REWRITE_VERSION = "1.0"
FAMILY = "role_lifted_object_rewrite"


class RoleLiftedRewriteError(ValueError):
    """Base class for invalid inputs and explicit abstentions."""


class RoleLiftedRewriteAbstention(RoleLiftedRewriteError):
    """Raised when the protected role interpretation is not unique."""


class RoleLiftedRewriteLimitError(RoleLiftedRewriteError):

    """Raised before a configured representation budget is exceeded."""


@dataclass(frozen=True)
class RoleLiftedRewriteLimits:
    """Hard bounds for the standalone compiler and renderer."""

    maximum_height: int = 30
    maximum_width: int = 30
    maximum_cells: int = 900
    maximum_palette: int = 10
    maximum_examples: int = 8
    maximum_tests: int = 8

    def to_record(self) -> Dict[str, int]:
        return {str(key): int(value) for key, value in asdict(self).items()}


DEFAULT_LIMITS = RoleLiftedRewriteLimits()


@dataclass(frozen=True)
class PayloadWorkspaceTrace:
    """Coordinate-free evidence for one runtime role binding."""

    axis: str
    workspace_direction: str
    half_depth: int
    transverse_span: int
    payload_palette_size: int
    modal_support: int
    modal_margin: int

    def to_record(self) -> Dict[str, object]:
        return {
            "axis": str(self.axis),
            "workspace_direction": str(self.workspace_direction),
            "half_depth": int(self.half_depth),
            "transverse_span": int(self.transverse_span),
            "payload_palette_size": int(self.payload_palette_size),
            "modal_support": int(self.modal_support),
            "modal_margin": int(self.modal_margin),
        }


@dataclass(frozen=True)
class RoleLiftedObjectRewriteProgram:
    """A color-free program whose parameters are rebound on every input."""

    selector: str = "CENTERED_SEPARATOR_PAYLOAD_WORKSPACE"
    source_role: str = "DOMINANT_PAYLOAD_COLOR"
    target_role: str = "WORKSPACE_OUTER_CENTER"
    effect: str = "WRITE_BOUND_SOURCE_COLOR"

    @property
    def semantic_key(self) -> str:
        return "|".join(
            (self.selector, self.source_role, self.target_role, self.effect)
        )

    @property
    def complexity(self) -> int:
        return 14

    def to_record(self) -> Dict[str, object]:
        """Return the persistent artifact.  It contains no resolved colors."""

        return {
            "schema": "komorebi.arc.role-lifted-object-rewrite.v1",
            "version": ROLE_LIFTED_REWRITE_VERSION,
            "selector": self.selector,
            "source_role": self.source_role,
            "target_role": self.target_role,
            "effect": self.effect,
            "semantic_key": self.semantic_key,
            "literal_color_free": True,
            "literal_coordinate_free": True,
            "task_identifier_free": True,
        }

    def apply(
        self,
        grid: Array,
        *,
        limits: RoleLiftedRewriteLimits = DEFAULT_LIMITS,
    ) -> Array:
        output, _ = apply_role_lifted_object_rewrite(grid, limits=limits)
        return output


@dataclass(frozen=True)
class RoleLiftedObjectRewriteCandidate:
    """Entry-independent exact candidate with auditable program provenance."""

    name: str
    program: RoleLiftedObjectRewriteProgram
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
            "metadata": _json_safe(dict(self.metadata)),
        }
        if include_grids:
            record["grids"] = [
                np.asarray(grid, dtype=np.int64).tolist() for grid in self.grids
            ]
            record["train_grids"] = [
                np.asarray(grid, dtype=np.int64).tolist()
                for grid in self.train_grids
            ]
        json.dumps(record, sort_keys=True)
        return record


@dataclass(frozen=True)
class _Interpretation:
    output: Array
    trace: PayloadWorkspaceTrace


def _json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"value is not JSON-safe: {type(value).__name__}")


def _validated_grid(grid: Array, limits: RoleLiftedRewriteLimits) -> Array:
    raw = np.asarray(grid)
    if raw.ndim != 2 or raw.size == 0:
        raise RoleLiftedRewriteError("rewrite analysis requires a nonempty 2D grid")
    height, width = raw.shape
    if height > limits.maximum_height or width > limits.maximum_width:
        raise RoleLiftedRewriteLimitError(
            f"grid shape {raw.shape} exceeds "
            f"{limits.maximum_height}x{limits.maximum_width}"
        )
    if raw.size > limits.maximum_cells:
        raise RoleLiftedRewriteLimitError("cell budget exceeded")
    if not np.issubdtype(raw.dtype, np.integer):
        if not np.all(np.equal(raw, np.floor(raw))):
            raise RoleLiftedRewriteError("grid values must be integers")
    value = np.asarray(raw, dtype=np.int16)
    palette = np.unique(value)
    if len(palette) > limits.maximum_palette:
        raise RoleLiftedRewriteLimitError("palette budget exceeded")
    if int(palette.min()) < 0 or int(palette.max()) > 9:
        raise RoleLiftedRewriteError("ARC colors must lie in [0, 9]")
    return np.ascontiguousarray(value)


def _unique_mode(values: Array) -> int | None:
    colors, counts = np.unique(np.asarray(values), return_counts=True)
    maximum = int(counts.max())
    winners = colors[counts == maximum]
    if len(winners) != 1:
        return None
    return int(winners[0])


def _infer_background(grid: Array) -> int:
    global_mode = _unique_mode(grid)
    if global_mode is not None:
        return global_mode
    border = np.concatenate(
        (grid[0, :], grid[-1, :], grid[1:-1, 0], grid[1:-1, -1])
    )
    border_mode = _unique_mode(border)
    if border_mode is None:
        raise RoleLiftedRewriteAbstention("background role is ambiguous")
    return border_mode


def _payload_mode(
    payload: Array,
    *,
    background: int,
    separator_color: int,
) -> Tuple[int, int, int, int]:
    if np.any(payload == background) or np.any(payload == separator_color):
        raise RoleLiftedRewriteAbstention(
            "payload must be filled and disjoint from separator and background"
        )
    colors, counts = np.unique(payload, return_counts=True)
    if len(colors) < 2:
        raise RoleLiftedRewriteAbstention("payload must be genuinely multicolor")
    order = np.argsort(counts)[::-1]
    best = int(counts[order[0]])
    second = int(counts[order[1]])
    if best <= second:
        raise RoleLiftedRewriteAbstention("payload has no unique modal color")
    return int(colors[order[0]]), best, best - second, int(len(colors))


def _horizontal_interpretation(
    grid: Array,
    *,
    background: int,
) -> _Interpretation | None:
    height, width = grid.shape
    if height < 3 or height % 2 == 0 or width % 2 == 0:
        return None
    middle = height // 2
    row = grid[middle, :]
    if len(np.unique(row)) != 1:
        return None
    separator_color = int(row[0])
    if separator_color == background:
        return None
    halves = (
        (grid[:middle, :], grid[middle + 1 :, :], "toward_bottom", (height - 1, width // 2)),
        (grid[middle + 1 :, :], grid[:middle, :], "toward_top", (0, width // 2)),
    )
    interpretations = []
    for payload, workspace, direction, target in halves:
        if not np.all(workspace == background):
            continue
        try:
            bound_color, support, margin, palette_size = _payload_mode(
                payload,
                background=background,
                separator_color=separator_color,
            )
        except RoleLiftedRewriteAbstention:
            continue
        if int(grid[target]) != background:
            continue
        output = grid.copy()
        output[target] = bound_color
        interpretations.append(
            _Interpretation(
                output=output,
                trace=PayloadWorkspaceTrace(
                    axis="horizontal",
                    workspace_direction=direction,
                    half_depth=middle,
                    transverse_span=width,
                    payload_palette_size=palette_size,
                    modal_support=support,
                    modal_margin=margin,
                ),
            )
        )
    if len(interpretations) != 1:
        return None
    return interpretations[0]


def _vertical_interpretation(
    grid: Array,
    *,
    background: int,
) -> _Interpretation | None:
    height, width = grid.shape
    if width < 3 or width % 2 == 0 or height % 2 == 0:
        return None
    middle = width // 2
    column = grid[:, middle]
    if len(np.unique(column)) != 1:
        return None
    separator_color = int(column[0])
    if separator_color == background:
        return None
    halves = (
        (grid[:, :middle], grid[:, middle + 1 :], "toward_right", (height // 2, width - 1)),
        (grid[:, middle + 1 :], grid[:, :middle], "toward_left", (height // 2, 0)),
    )
    interpretations = []
    for payload, workspace, direction, target in halves:
        if not np.all(workspace == background):
            continue
        try:
            bound_color, support, margin, palette_size = _payload_mode(
                payload,
                background=background,
                separator_color=separator_color,
            )
        except RoleLiftedRewriteAbstention:
            continue
        if int(grid[target]) != background:
            continue
        output = grid.copy()
        output[target] = bound_color
        interpretations.append(
            _Interpretation(
                output=output,
                trace=PayloadWorkspaceTrace(
                    axis="vertical",
                    workspace_direction=direction,
                    half_depth=middle,
                    transverse_span=height,
                    payload_palette_size=palette_size,
                    modal_support=support,
                    modal_margin=margin,
                ),
            )
        )
    if len(interpretations) != 1:
        return None
    return interpretations[0]


def apply_role_lifted_object_rewrite(
    grid: Array,
    *,
    limits: RoleLiftedRewriteLimits = DEFAULT_LIMITS,
) -> Tuple[Array, PayloadWorkspaceTrace]:
    """Bind the scene roles and execute the unique protected interpretation."""

    source = _validated_grid(grid, limits)
    background = _infer_background(source)
    interpretations = [
        item
        for item in (
            _horizontal_interpretation(source, background=background),
            _vertical_interpretation(source, background=background),
        )
        if item is not None
    ]
    if len(interpretations) != 1:
        raise RoleLiftedRewriteAbstention(
            "scene does not have one unique payload-workspace interpretation"
        )
    result = interpretations[0]
    if np.array_equal(result.output, source):
        raise RoleLiftedRewriteAbstention("role rewrite produced no change")
    return np.ascontiguousarray(result.output), result.trace


def _exact(left: Array, right: Array) -> bool:
    return bool(np.array_equal(np.asarray(left), np.asarray(right)))


def compile_role_lifted_object_rewrite(
    train: Sequence[Tuple[Array, Array]],
    tests: Sequence[Array],
    *,
    limits: RoleLiftedRewriteLimits = DEFAULT_LIMITS,
) -> Tuple[RoleLiftedObjectRewriteCandidate, ...]:
    """Compile the fixed schema only after exact fit and full LOO rebinding.

    Demonstration outputs are used only to accept or reject the color-free
    schema.  Every source color and target cell is rebound from each input.
    Test outputs are never consulted.
    """

    if len(train) < 2:
        return ()
    if len(train) > limits.maximum_examples or len(tests) > limits.maximum_tests:
        raise RoleLiftedRewriteLimitError("example budget exceeded")

    program = RoleLiftedObjectRewriteProgram()
    train_predictions = []
    traces = []
    validated_train = []
    try:
        for source, target in train:
            source_grid = _validated_grid(source, limits)
            target_grid = _validated_grid(target, limits)
            if source_grid.shape != target_grid.shape:
                return ()
            prediction, trace = apply_role_lifted_object_rewrite(
                source_grid,
                limits=limits,
            )
            if not _exact(prediction, target_grid):
                return ()
            validated_train.append((source_grid, target_grid))
            train_predictions.append(prediction)
            traces.append(trace)
    except RoleLiftedRewriteError:
        return ()

    # Recompile from every proper training fold.  The schema has no learned
    # literal parameters, but this explicit loop checks that each held source
    # can independently rebind the roles and recover its target.
    loo_exact_count = 0
    for held_index, (held_source, held_target) in enumerate(validated_train):
        fold = [
            example
            for example_index, example in enumerate(validated_train)
            if example_index != held_index
        ]
        if not fold:
            continue
        try:
            if not all(
                _exact(program.apply(source, limits=limits), target)
                for source, target in fold
            ):
                continue
            held_prediction = program.apply(held_source, limits=limits)
        except RoleLiftedRewriteError:
            continue
        loo_exact_count += int(_exact(held_prediction, held_target))
    if loo_exact_count != len(validated_train):
        return ()

    test_predictions = []
    try:
        for test in tests:
            test_predictions.append(program.apply(test, limits=limits))
    except RoleLiftedRewriteError:
        return ()

    trace_records = [trace.to_record() for trace in traces]
    metadata: Dict[str, object] = {
        "schema": "komorebi.arc.role-lifted-candidate.v1",
        "program": program.to_record(),
        "program_version": ROLE_LIFTED_REWRITE_VERSION,
        "role_binding": "input_local_rebinding",
        "source_role": "unique_modal_payload_color",
        "target_role": "far_center_of_equal_blank_workspace",
        "effect_binding": "write_bound_source_color",
        "exact_demonstration_contract": True,
        "test_target_isolation": True,
        "task_identifier_free": True,
        "literal_color_free_program": True,
        "literal_coordinate_free_program": True,
        "palette_equivariant": True,
        "d4_equivariant": True,
        "witness_protocol": "leave_one_demonstration_out_role_rebinding",
        "loo_exact_count": int(loo_exact_count),
        "loo_total_count": int(len(validated_train)),
        "witness_reconstructible": True,
        "minimum_modal_margin": int(
            min(trace.modal_margin for trace in traces)
        ),
        "training_trace_summary": trace_records,
        "limits": limits.to_record(),
    }
    return (
        RoleLiftedObjectRewriteCandidate(
            name="role_lifted:dominant_payload_to_workspace_outer_center",
            program=program,
            grids=tuple(test_predictions),
            train_grids=tuple(train_predictions),
            complexity=program.complexity,
            metadata=metadata,
        ),
    )


role_lifted_object_rewrite_candidates = compile_role_lifted_object_rewrite


__all__ = [
    "DEFAULT_LIMITS",
    "FAMILY",
    "PayloadWorkspaceTrace",
    "ROLE_LIFTED_REWRITE_VERSION",
    "RoleLiftedObjectRewriteCandidate",
    "RoleLiftedObjectRewriteProgram",
    "RoleLiftedRewriteAbstention",
    "RoleLiftedRewriteError",
    "RoleLiftedRewriteLimitError",
    "RoleLiftedRewriteLimits",
    "apply_role_lifted_object_rewrite",
    "compile_role_lifted_object_rewrite",
    "role_lifted_object_rewrite_candidates",
]
