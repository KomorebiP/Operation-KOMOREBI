"""Finite role-parametric action-schema synthesis for PR-LASM Block 11.

The compiler boundary is deliberately narrow: a caller supplies one raw ARC
task or an already sanitized :class:`TrainingTask`; labelled demonstrations
may constrain typed holes, while test records contribute only their ``input``
grid.  Candidate programs are target-free ``ToolProgram`` values before any
test input is executed.

Every member of the declared finite grammar is enumerated.  Programs must
replay every demonstration exactly, after which their test executions are
quotiented by exact raster behavior.  A prediction is exposed only when one
behavior class remains; syntactic multiplicity is harmless, behavioral
ambiguity causes abstention.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from komorebi_lasm_action.tools import TOOL_LANGUAGE_HASH, ToolProgram, execute_tool
from komorebi_lasm_composition.model import (
    Grid,
    canonical_value,
    sha256_record,
)
from komorebi_lasm_composition.task import TrainingTask, sanitize_training_task


SCHEMA_VERSION = 1
STABLE = "stable_for_next_frozen_corpus"
PROVISIONAL = "provisional"
_EXECUTION_ERRORS = (
    AssertionError,
    KeyError,
    RuntimeError,
    TypeError,
    ValueError,
    OverflowError,
)


@dataclass(frozen=True, slots=True)
class ActionSchemaLimits:
    """Finite task and syntax bounds; reaching one forces abstention."""

    max_training_examples: int = 10
    max_test_examples: int = 10
    max_programs: int = 16_384

    def __post_init__(self) -> None:
        for name in ("max_training_examples", "max_test_examples", "max_programs"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")

    def to_record(self) -> dict[str, Any]:
        return {
            "max_training_examples": self.max_training_examples,
            "max_test_examples": self.max_test_examples,
            "max_programs": self.max_programs,
        }


DEFAULT_ACTION_LIMITS = ActionSchemaLimits()


@dataclass(frozen=True, slots=True)
class TypedHole:
    """One finite or source-derived coordinate in an action schema."""

    name: str
    value_type: str
    domain: tuple[Any, ...] = ()
    derived_from: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("hole name must be a nonempty string")
        if not isinstance(self.value_type, str) or not self.value_type:
            raise ValueError("hole value_type must be a nonempty string")
        object.__setattr__(self, "domain", tuple(self.domain))
        if not self.domain and self.derived_from is None:
            raise ValueError("a typed hole needs a finite domain or derivation")
        if self.derived_from is not None and (
            not isinstance(self.derived_from, str) or not self.derived_from
        ):
            raise ValueError("derived_from must be a nonempty string when present")

    def to_record(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "value_type": self.value_type,
        }
        if self.domain:
            result["domain"] = canonical_value(self.domain)
        if self.derived_from is not None:
            result["derived_from"] = self.derived_from
        return result


@dataclass(frozen=True, slots=True)
class ActionSchema:
    """A typed, task-independent anti-unification of action programs."""

    name: str
    status: str
    input_type: str
    output_type: str
    fixed_axes: tuple[tuple[str, Any], ...]
    holes: tuple[TypedHole, ...]
    residual_routes: tuple[str, ...]
    minimum_distinct_support: int
    observed_wrong_unique: int

    def __post_init__(self) -> None:
        if self.status not in {STABLE, PROVISIONAL}:
            raise ValueError("schema status must be stable or provisional")
        if self.input_type != "grid" or self.output_type != "grid":
            raise ValueError("action schemas must have grid -> grid type")
        object.__setattr__(self, "fixed_axes", tuple(self.fixed_axes))
        object.__setattr__(self, "holes", tuple(self.holes))
        object.__setattr__(self, "residual_routes", tuple(self.residual_routes))
        if not self.name or not self.holes or not self.residual_routes:
            raise ValueError("schema name, holes, and routes must be nonempty")
        if self.minimum_distinct_support < 1:
            raise ValueError("minimum_distinct_support must be positive")
        if self.observed_wrong_unique != 0:
            raise ValueError("a packaged schema cannot have a wrong unique activation")

    @property
    def schema_hash(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.block11.action_schema",
            "schema_version": SCHEMA_VERSION,
            "name": self.name,
            "status": self.status,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "fixed_axes": {key: canonical_value(value) for key, value in self.fixed_axes},
            "holes": [hole.to_record() for hole in self.holes],
            "residual_routes": list(self.residual_routes),
            "promotion_contract": {
                "minimum_distinct_support": self.minimum_distinct_support,
                "maximum_wrong_unique_activations": self.observed_wrong_unique,
            },
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record, "schema_hash": self.schema_hash}


def _derived(name: str, value_type: str, source: str) -> TypedHole:
    return TypedHole(name, value_type, derived_from=source)


ACTION_SCHEMAS = (
    ActionSchema(
        name="role_component_support_edit",
        status=STABLE,
        input_type="grid",
        output_type="grid",
        fixed_axes=(("geometry", "selected_support"), ("closure", "once")),
        holes=(
            TypedHole("selector", "component_selector", (
                "all_components", "singleton_components", "non_singleton_components",
                "smallest_components", "largest_components", "with_holes",
                "without_holes", "border_touching", "interior_components",
                "unique_shape_components", "repeated_shape_components",
                "shape_matched_components", "color_components", "all_foreground_cells",
            )),
            _derived("background_role", "color_role", "training inputs"),
            _derived("selector_color_role", "color_role", "training inputs"),
            TypedHole("connectivity", "connectivity", (4, 8)),
            TypedHole("monochrome_components", "boolean", (False, True)),
            TypedHole("effect", "support_effect", ("erase_selected", "recolor_selected")),
            _derived("paint_role", "color_role", "demonstrated changed-to color"),
        ),
        residual_routes=("support_removal", "same_support_recolor"),
        minimum_distinct_support=2,
        observed_wrong_unique=0,
    ),
    ActionSchema(
        name="role_pair_relation_constructor",
        status=STABLE,
        input_type="grid",
        output_type="grid",
        fixed_axes=(("closure", "once"), ("background_only", True)),
        holes=(
            TypedHole("selector", "component_selector", (
                "all_components", "singleton_components", "color_components",
            )),
            _derived("background_role", "color_role", "training inputs"),
            _derived("selector_color_role", "color_role", "training inputs"),
            TypedHole("relation", "object_relation", (
                "aligned_pairs", "same_color_aligned_pairs", "same_shape_aligned_pairs",
                "diagonal_pairs", "same_shape_diagonal_pairs",
            )),
            TypedHole("geometry", "finite_locus", (
                "between_extents", "diagonal_between_extents", "pair_midpoint_stamp",
            )),
            TypedHole("stamp", "cell_offset_set", (
                "point", "orthogonal_plus", "diagonal_plus", "moore",
            )),
            TypedHole("effect", "paint_effect", ("paint_source_color", "paint_constant")),
            _derived("paint_role", "color_role", "source or demonstrated changed-to color"),
        ),
        residual_routes=("support_addition",),
        minimum_distinct_support=2,
        observed_wrong_unique=0,
    ),
    ActionSchema(
        name="role_component_box_render",
        status=PROVISIONAL,
        input_type="grid",
        output_type="grid",
        fixed_axes=(("relation", "none"), ("closure", "once")),
        holes=(
            TypedHole("selector", "component_selector", (
                "all_components", "with_holes", "without_holes", "color_components",
                "smallest_components", "largest_components", "unique_shape_components",
                "repeated_shape_components",
            )),
            _derived("background_role", "color_role", "training inputs"),
            _derived("selector_color_role", "color_role", "training inputs"),
            TypedHole("connectivity", "connectivity", (4, 8)),
            TypedHole("monochrome_components", "boolean", (False, True)),
            TypedHole("geometry", "box_geometry", ("bounding_box_fill", "bounding_box_outline")),
            TypedHole("effect", "paint_effect", ("paint_source_color", "paint_constant")),
            _derived("paint_role", "color_role", "source or demonstrated changed-to color"),
            TypedHole("background_only", "boolean", (False, True)),
        ),
        residual_routes=("support_addition",),
        minimum_distinct_support=2,
        observed_wrong_unique=0,
    ),
)
ACTION_SCHEMAS_BY_NAME = MappingProxyType({schema.name: schema for schema in ACTION_SCHEMAS})
ACTION_SCHEMA_GRAMMAR_HASH = sha256_record({
    "schema": "komorebi.block11.action_schema_grammar",
    "schema_version": SCHEMA_VERSION,
    "schemas": [schema.semantic_record for schema in ACTION_SCHEMAS],
    "background_coordinate_routing": "per_candidate_background_role",
    "behavior_selection": "complete_exact_raster_quotient",
    "tool_language_hash": TOOL_LANGUAGE_HASH,
})


@dataclass(frozen=True, slots=True)
class SchemaProgram:
    """One executable program together with the schemas that generated it."""

    program: ToolProgram
    schemas: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.program, ToolProgram):
            raise TypeError("program must be a ToolProgram")
        object.__setattr__(self, "schemas", tuple(sorted(set(self.schemas))))
        if not self.schemas or any(name not in ACTION_SCHEMAS_BY_NAME for name in self.schemas):
            raise ValueError("schemas must name packaged action schemas")

    def to_record(self) -> dict[str, Any]:
        return {"schemas": list(self.schemas), "program": self.program.to_record()}


@dataclass(frozen=True, slots=True)
class SchemaEnumeration:
    """Complete finite syntax enumeration and its deterministic certificate."""

    programs: tuple[SchemaProgram, ...]
    source_hash: str
    training_hashes: tuple[str, ...]
    residual_modes: tuple[str, ...]
    program_space_hash: str
    complete: bool = True
    truncation_reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "programs", tuple(self.programs))
        object.__setattr__(self, "training_hashes", tuple(self.training_hashes))
        object.__setattr__(self, "residual_modes", tuple(self.residual_modes))
        expected = sha256_record([item.program.tool_id for item in self.programs])
        if self.program_space_hash != expected:
            raise ValueError("program_space_hash does not match enumeration")
        if not isinstance(self.complete, bool):
            raise TypeError("complete must be Boolean")
        if self.complete == bool(self.truncation_reason):
            raise ValueError("only incomplete enumerations may carry a truncation reason")

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.block11.action_schema_enumeration",
            "schema_version": SCHEMA_VERSION,
            "source_hash": self.source_hash,
            "training_hashes": list(self.training_hashes),
            "grammar_hash": ACTION_SCHEMA_GRAMMAR_HASH,
            "residual_modes": list(self.residual_modes),
            "programs_enumerated": len(self.programs),
            "program_space_hash": self.program_space_hash,
            "complete": self.complete,
            "truncation_reason": self.truncation_reason,
        }


@dataclass(frozen=True, slots=True)
class RasterBehavior:
    """One exact test-output behavior shared by one or more programs."""

    behavior_hash: str
    outputs: tuple[Grid, ...]
    equivalent_program_ids: tuple[str, ...]
    schemas: tuple[str, ...]
    representative: ToolProgram

    def __post_init__(self) -> None:
        object.__setattr__(self, "outputs", tuple(self.outputs))
        object.__setattr__(self, "equivalent_program_ids", tuple(self.equivalent_program_ids))
        object.__setattr__(self, "schemas", tuple(self.schemas))
        if self.behavior_hash != sha256_record(self.outputs):
            raise ValueError("behavior hash does not match exact raster outputs")
        if not self.equivalent_program_ids or not self.schemas:
            raise ValueError("a behavior needs supporting programs and schemas")

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "outputs": canonical_value(self.outputs),
            "equivalent_program_ids": list(self.equivalent_program_ids),
            "schemas": list(self.schemas),
            "representative_program": self.representative.to_record(),
        }


@dataclass(frozen=True, slots=True)
class SchemaWorkReceipt:
    """Exact work and completeness accounting for one compilation."""

    source_hash: str
    training_hashes: tuple[str, ...]
    grammar_hash: str
    program_space_hash: str
    programs_enumerated: int
    demonstration_executions: int
    training_exact_programs: int
    admitted_exact_programs: int
    test_executions: int
    test_executable_programs: int
    behavior_classes: int
    execution_errors: int
    enumeration_complete: bool
    truncation_reason: str = ""
    provisional_admitted: bool = True

    @property
    def receipt_hash(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.block11.action_schema_work_receipt",
            "schema_version": SCHEMA_VERSION,
            "source_hash": self.source_hash,
            "training_hashes": list(self.training_hashes),
            "grammar_hash": self.grammar_hash,
            "program_space_hash": self.program_space_hash,
            "programs_enumerated": self.programs_enumerated,
            "demonstration_executions": self.demonstration_executions,
            "training_exact_programs": self.training_exact_programs,
            "admitted_exact_programs": self.admitted_exact_programs,
            "test_executions": self.test_executions,
            "test_executable_programs": self.test_executable_programs,
            "behavior_classes": self.behavior_classes,
            "execution_errors": self.execution_errors,
            "enumeration_complete": self.enumeration_complete,
            "truncation_reason": self.truncation_reason,
            "provisional_admitted": self.provisional_admitted,
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record, "receipt_hash": self.receipt_hash}


@dataclass(frozen=True, slots=True)
class ActionSchemaCompilation:
    """Behavior-quotiented result for one sanitized training task."""

    behaviors: tuple[RasterBehavior, ...]
    receipt: SchemaWorkReceipt

    def __post_init__(self) -> None:
        object.__setattr__(self, "behaviors", tuple(self.behaviors))
        if self.receipt.behavior_classes != len(self.behaviors):
            raise ValueError("receipt behavior count does not match result")

    @property
    def status(self) -> str:
        if not self.receipt.enumeration_complete:
            return "incomplete_abstention"
        if not self.behaviors:
            return "no_candidate"
        if len(self.behaviors) == 1:
            return "unique"
        return "ambiguous"

    @property
    def prediction(self) -> tuple[Grid, ...] | None:
        return self.behaviors[0].outputs if len(self.behaviors) == 1 else None

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.block11.action_schema_compilation",
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "behaviors": [behavior.to_record() for behavior in self.behaviors],
            "receipt": self.receipt.to_record(),
        }


def _array(grid: Grid) -> np.ndarray:
    return np.asarray(grid, dtype=np.int16)


def _resolve_role(
    array: np.ndarray,
    role: str,
    *,
    background: int | None = None,
    source: int | None = None,
) -> int:
    if role.startswith("literal:"):
        value = int(role.split(":", 1)[1])
        if not 0 <= value <= 9:
            raise ValueError("literal color is outside the ARC palette")
        return value
    if role == "source":
        if source is None:
            raise ValueError("source color role is unavailable")
        return int(source)
    if role == "zero":
        return 0
    counts = Counter(int(value) for value in array.ravel())
    if role == "corner":
        corners = Counter((
            int(array[0, 0]), int(array[0, -1]),
            int(array[-1, 0]), int(array[-1, -1]),
        ))
        maximum = max(corners.values())
        winners = sorted(color for color, count in corners.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("corner color is ambiguous")
        return winners[0]
    if role == "background":
        if background is not None:
            return int(background)
        maximum = max(counts.values())
        winners = sorted(color for color, count in counts.items() if count == maximum)
        if len(winners) != 1:
            raise ValueError("background color is ambiguous")
        return winners[0]
    resolved_background = (
        int(background) if background is not None else _resolve_role(array, "background")
    )
    foreground = {color: count for color, count in counts.items() if color != resolved_background}
    if not foreground:
        raise ValueError("foreground role is unavailable")
    if role == "unique_foreground":
        if len(foreground) != 1:
            raise ValueError("unique foreground color is ambiguous")
        return next(iter(foreground))
    if role not in {"rarest_foreground", "most_foreground"}:
        raise ValueError(f"unknown color role {role!r}")
    wanted = min(foreground.values()) if role == "rarest_foreground" else max(foreground.values())
    winners = sorted(color for color, count in foreground.items() if count == wanted)
    if len(winners) != 1:
        raise ValueError(f"{role} color is ambiguous")
    return winners[0]


def _deduplicate_roles(roles: Iterable[str], inputs: tuple[Grid, ...]) -> tuple[str, ...]:
    priority = {
        "background": 0,
        "corner": 1,
        "unique_foreground": 2,
        "rarest_foreground": 3,
        "most_foreground": 4,
        "zero": 5,
        "source": 6,
    }
    result: dict[tuple[Any, ...], str] = {}
    for role in roles:
        try:
            behavior = ("source",) if role == "source" else tuple(
                _resolve_role(_array(grid), role) for grid in inputs
            )
        except (TypeError, ValueError):
            continue
        prior = result.get(behavior)
        rank = (priority.get(role, 20), role)
        if prior is None or rank < (priority.get(prior, 20), prior):
            result[behavior] = role
    return tuple(sorted(result.values(), key=lambda role: (priority.get(role, 20), role)))


def _common_colors(inputs: tuple[Grid, ...]) -> tuple[int, ...]:
    common = {value for row in inputs[0] for value in row}
    for grid in inputs[1:]:
        common &= {value for row in grid for value in row}
    return tuple(sorted(common))


def _background_roles(inputs: tuple[Grid, ...]) -> tuple[str, ...]:
    roles: list[str] = []
    for role in ("background", "corner", "zero"):
        try:
            tuple(_resolve_role(_array(grid), role) for grid in inputs)
        except ValueError:
            continue
        roles.append(role)
    roles.extend(f"literal:{color}" for color in _common_colors(inputs))
    return tuple(dict.fromkeys(roles))


def _paint_roles(inputs: tuple[Grid, ...], targets: tuple[Grid, ...]) -> tuple[str, ...]:
    changed_target_colors: set[int] | None = None
    for source_grid, target_grid in zip(inputs, targets):
        source = _array(source_grid)
        target = _array(target_grid)
        if source.shape != target.shape:
            return ()
        colors = {int(value) for value in target[source != target]}
        changed_target_colors = colors if changed_target_colors is None else changed_target_colors & colors
    roles: list[str] = [f"literal:{color}" for color in sorted(changed_target_colors or ())]
    for role in (
        "unique_foreground", "rarest_foreground", "most_foreground", "background", "zero",
    ):
        try:
            tuple(_resolve_role(_array(grid), role) for grid in inputs)
        except ValueError:
            continue
        roles.append(role)
    roles.append("source")
    return tuple(dict.fromkeys(roles))


def _selector_color_roles(inputs: tuple[Grid, ...]) -> tuple[str, ...]:
    roles: list[str] = []
    for role in ("unique_foreground", "rarest_foreground", "most_foreground"):
        try:
            tuple(_resolve_role(_array(grid), role) for grid in inputs)
        except ValueError:
            continue
        roles.append(role)
    roles.extend(f"literal:{color}" for color in _common_colors(inputs))
    return tuple(dict.fromkeys(roles)) or ("unique_foreground",)


def _consistent_constant_paints(
    roles: Iterable[str],
    inputs: tuple[Grid, ...],
    targets: tuple[Grid, ...],
) -> tuple[str, ...]:
    result: list[str] = []
    for role in roles:
        if role == "source":
            continue
        valid = True
        for source_grid, target_grid in zip(inputs, targets):
            source = _array(source_grid)
            target = _array(target_grid)
            changed_colors = {int(value) for value in target[source != target]}
            if len(changed_colors) != 1:
                valid = False
                break
            try:
                resolved = _resolve_role(source, role)
            except ValueError:
                valid = False
                break
            if resolved != next(iter(changed_colors)):
                valid = False
                break
        if valid:
            result.append(role)
    return tuple(result)


def _residual_modes_for_background(
    task: TrainingTask, role: str,
) -> tuple[bool, bool, bool]:
    """Classify training edits in the coordinate system of one background role."""

    additions = removals = recolors = False
    for source_grid, target_grid in zip(task.training_inputs, task.training_outputs):
        source = _array(source_grid)
        target = _array(target_grid)
        background = _resolve_role(source, role)
        changed = source != target
        additions |= bool(((source == background) & (target != background) & changed).any())
        removals |= bool(((source != background) & (target == background) & changed).any())
        recolors |= bool(((source != background) & (target != background) & changed).any())
    return additions, removals, recolors


def _base_parameters(
    *,
    background_role: str,
    connectivity: int = 4,
    monochrome_components: bool = True,
    selector_color_role: str = "unique_foreground",
    paint_role: str = "literal:1",
    background_only: bool = True,
    stamp_offsets: Sequence[tuple[int, int]] = (),
) -> dict[str, Any]:
    return {
        "background_role": background_role,
        "connectivity": connectivity,
        "monochrome_components": monochrome_components,
        "selector_color_role": selector_color_role,
        "paint_role": paint_role,
        "background_only": background_only,
        "include_sources": True,
        "directions": [],
        "offset": [0, 0],
        "stamp_offsets": [list(item) for item in stamp_offsets],
        "max_steps": 30,
        "shape_mode": "exact",
    }


def _program(
    selector: str,
    relation: str,
    geometry: str,
    effect: str,
    parameters: Mapping[str, Any],
) -> ToolProgram | None:
    costs = {
        "selected_support": 3,
        "bounding_box_fill": 5,
        "bounding_box_outline": 5,
        "between_extents": 6,
        "diagonal_between_extents": 7,
        "pair_midpoint_stamp": 7,
    }
    try:
        return ToolProgram.from_parameters(
            selector=selector,
            relation=relation,
            geometry=geometry,
            effect=effect,
            closure="once",
            parameters=parameters,
            cost=costs[geometry],
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def _add_program(
    result: dict[str, tuple[ToolProgram, set[str]]],
    schema: str,
    program: ToolProgram | None,
) -> None:
    if program is None:
        return
    prior = result.get(program.tool_id)
    if prior is None:
        result[program.tool_id] = (program, {schema})
    else:
        prior[1].add(schema)


def enumerate_action_schema_programs(
    task: Mapping[str, Any] | TrainingTask,
    *,
    limits: ActionSchemaLimits | None = None,
) -> SchemaEnumeration:
    """Enumerate the complete declared schema grammar for one task.

    This function uses labelled demonstrations to bind holes but never executes
    a program on a test input.  The returned programs are immutable and
    target-free.  Empty, complete enumerations are valid.
    """

    limits = limits or DEFAULT_ACTION_LIMITS
    if not isinstance(limits, ActionSchemaLimits):
        raise TypeError("limits must be an ActionSchemaLimits record")
    sanitized = sanitize_training_task(task)
    inputs = sanitized.training_inputs
    targets = sanitized.training_outputs
    input_limit = ""
    if len(inputs) > limits.max_training_examples:
        input_limit = "training_example_limit"
    elif len(sanitized.test_inputs) > limits.max_test_examples:
        input_limit = "test_example_limit"
    if input_limit:
        return SchemaEnumeration(
            programs=(),
            source_hash=sanitized.source_hash,
            training_hashes=sanitized.training_hashes,
            residual_modes=(),
            program_space_hash=sha256_record([]),
            complete=False,
            truncation_reason=input_limit,
        )
    programs: dict[str, tuple[ToolProgram, set[str]]] = {}
    modes: tuple[str, ...] = ()

    if all(
        (len(source), len(source[0])) == (len(target), len(target[0]))
        for source, target in zip(inputs, targets)
    ):
        backgrounds = _deduplicate_roles(_background_roles(inputs), inputs)
        paints = _consistent_constant_paints(
            _deduplicate_roles(_paint_roles(inputs, targets), inputs), inputs, targets,
        )
        selector_roles = _deduplicate_roles(_selector_color_roles(inputs), inputs)
        background_modes = {
            background: _residual_modes_for_background(sanitized, background)
            for background in backgrounds
        }
        additions = any(value[0] for value in background_modes.values())
        removals = any(value[1] for value in background_modes.values())
        recolors = any(value[2] for value in background_modes.values())
        modes = tuple(
            name for name, active in (
                ("support_addition", additions),
                ("support_removal", removals),
                ("same_support_recolor", recolors),
            ) if active
        )

        support_selectors = (
            "all_components", "singleton_components", "non_singleton_components",
            "smallest_components", "largest_components", "with_holes", "without_holes",
            "border_touching", "interior_components", "unique_shape_components",
            "repeated_shape_components", "shape_matched_components", "color_components",
            "all_foreground_cells",
        )
        for background in backgrounds:
            _, background_removals, background_recolors = background_modes[background]
            for connectivity in (4, 8):
                for monochrome in (False, True):
                    for selector in support_selectors:
                        roles = selector_roles if selector == "color_components" else ("unique_foreground",)
                        for selector_role in roles:
                            base = _base_parameters(
                                background_role=background,
                                connectivity=connectivity,
                                monochrome_components=monochrome,
                                selector_color_role=selector_role,
                                paint_role="source",
                                background_only=False,
                            )
                            if background_removals:
                                _add_program(
                                    programs,
                                    "role_component_support_edit",
                                    _program(selector, "none", "selected_support", "erase_selected", base),
                                )
                            if background_recolors:
                                for paint in paints:
                                    parameters = dict(base)
                                    parameters["paint_role"] = paint
                                    _add_program(
                                        programs,
                                        "role_component_support_edit",
                                        _program(
                                            selector, "none", "selected_support",
                                            "recolor_selected", parameters,
                                        ),
                                    )

        box_selectors = (
            "all_components", "with_holes", "without_holes", "color_components",
            "smallest_components", "largest_components", "unique_shape_components",
            "repeated_shape_components",
        )
        for background in backgrounds:
            background_additions, _, _ = background_modes[background]
            if not background_additions:
                continue
            for connectivity in (4, 8):
                for monochrome in (False, True):
                    for selector in box_selectors:
                        roles = selector_roles if selector == "color_components" else ("unique_foreground",)
                        for selector_role in roles:
                            for geometry in ("bounding_box_fill", "bounding_box_outline"):
                                for background_only in (False, True):
                                    base = _base_parameters(
                                        background_role=background,
                                        connectivity=connectivity,
                                        monochrome_components=monochrome,
                                        selector_color_role=selector_role,
                                        paint_role="source",
                                        background_only=background_only,
                                    )
                                    _add_program(
                                        programs,
                                        "role_component_box_render",
                                        _program(
                                            selector, "none", geometry,
                                            "paint_source_color", base,
                                        ),
                                    )
                                    for paint in paints:
                                        parameters = dict(base)
                                        parameters["paint_role"] = paint
                                        _add_program(
                                            programs,
                                            "role_component_box_render",
                                            _program(
                                                selector, "none", geometry,
                                                "paint_constant", parameters,
                                            ),
                                        )

        pair_selectors = ("all_components", "singleton_components", "color_components")
        relations = (
            "aligned_pairs", "same_color_aligned_pairs", "same_shape_aligned_pairs",
            "diagonal_pairs", "same_shape_diagonal_pairs",
        )
        stamps = (
            ((0, 0),),
            ((0, 0), (-1, 0), (0, -1), (0, 1), (1, 0)),
            ((0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)),
            (
                (0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1),
                (0, 1), (1, -1), (1, 0), (1, 1),
            ),
        )
        for background in backgrounds:
            background_additions, _, _ = background_modes[background]
            if not background_additions:
                continue
            for selector in pair_selectors:
                roles = selector_roles if selector == "color_components" else ("unique_foreground",)
                for selector_role in roles:
                    for relation in relations:
                        if "diagonal" in relation:
                            geometries: tuple[tuple[str, tuple[tuple[int, int], ...]], ...] = (
                                ("diagonal_between_extents", ()),
                            )
                        else:
                            geometries = (
                                ("between_extents", ()),
                                *(("pair_midpoint_stamp", stamp) for stamp in stamps),
                            )
                        for geometry, stamp in geometries:
                            for effect in ("paint_source_color", "paint_constant"):
                                effect_paints = ("source",) if effect == "paint_source_color" else paints
                                for paint in effect_paints:
                                    parameters = _base_parameters(
                                        background_role=background,
                                        selector_color_role=selector_role,
                                        paint_role=paint,
                                        background_only=True,
                                        stamp_offsets=stamp,
                                    )
                                    _add_program(
                                        programs,
                                        "role_pair_relation_constructor",
                                        _program(selector, relation, geometry, effect, parameters),
                                    )

    ordered = tuple(
        SchemaProgram(program, tuple(sorted(schemas)))
        for program, schemas in sorted(
            programs.values(), key=lambda item: (item[0].cost, item[0].tool_id)
        )
    )
    complete = len(ordered) <= limits.max_programs
    return SchemaEnumeration(
        programs=ordered,
        source_hash=sanitized.source_hash,
        training_hashes=sanitized.training_hashes,
        residual_modes=modes,
        program_space_hash=sha256_record([item.program.tool_id for item in ordered]),
        complete=complete,
        truncation_reason="" if complete else "program_enumeration_limit",
    )


def compile_action_schemas(
    task: Mapping[str, Any] | TrainingTask,
    *,
    limits: ActionSchemaLimits | None = None,
    allow_provisional: bool = True,
) -> ActionSchemaCompilation:
    """Compile one task with exact-demo replay and exact-raster quotienting."""

    sanitized = sanitize_training_task(task)
    if not isinstance(allow_provisional, bool):
        raise TypeError("allow_provisional must be Boolean")
    enumeration = enumerate_action_schema_programs(sanitized, limits=limits)
    if not enumeration.complete:
        receipt = SchemaWorkReceipt(
            source_hash=sanitized.source_hash,
            training_hashes=sanitized.training_hashes,
            grammar_hash=ACTION_SCHEMA_GRAMMAR_HASH,
            program_space_hash=enumeration.program_space_hash,
            programs_enumerated=len(enumeration.programs),
            demonstration_executions=0,
            training_exact_programs=0,
            admitted_exact_programs=0,
            test_executions=0,
            test_executable_programs=0,
            behavior_classes=0,
            execution_errors=0,
            enumeration_complete=False,
            truncation_reason=enumeration.truncation_reason,
            provisional_admitted=allow_provisional,
        )
        return ActionSchemaCompilation((), receipt)
    demonstration_executions = 0
    execution_errors = 0
    exact: list[SchemaProgram] = []
    for item in enumeration.programs:
        outputs: list[Grid] = []
        failed = False
        for grid in sanitized.training_inputs:
            demonstration_executions += 1
            try:
                outputs.append(execute_tool(item.program, grid))
            except _EXECUTION_ERRORS:
                execution_errors += 1
                failed = True
                break
        if not failed and tuple(outputs) == sanitized.training_outputs:
            exact.append(item)

    admitted: list[SchemaProgram] = []
    for item in exact:
        names = tuple(
            name for name in item.schemas
            if allow_provisional or ACTION_SCHEMAS_BY_NAME[name].status != PROVISIONAL
        )
        if names:
            admitted.append(SchemaProgram(item.program, names))

    grouped: dict[str, dict[str, Any]] = {}
    test_executions = 0
    test_executable_programs = 0
    for item in admitted:
        outputs = []
        failed = False
        for grid in sanitized.test_inputs:
            test_executions += 1
            try:
                outputs.append(execute_tool(item.program, grid))
            except _EXECUTION_ERRORS:
                execution_errors += 1
                failed = True
                break
        if failed:
            continue
        test_executable_programs += 1
        frozen_outputs = tuple(outputs)
        behavior_hash = sha256_record(frozen_outputs)
        group = grouped.setdefault(behavior_hash, {
            "outputs": frozen_outputs,
            "programs": [],
            "schemas": set(),
        })
        group["programs"].append(item.program)
        group["schemas"].update(item.schemas)

    behaviors: list[RasterBehavior] = []
    for behavior_hash, group in sorted(grouped.items()):
        programs = tuple(sorted(group["programs"], key=lambda value: (value.cost, value.tool_id)))
        behaviors.append(RasterBehavior(
            behavior_hash=behavior_hash,
            outputs=group["outputs"],
            equivalent_program_ids=tuple(program.tool_id for program in programs),
            schemas=tuple(sorted(group["schemas"])),
            representative=programs[0],
        ))

    receipt = SchemaWorkReceipt(
        source_hash=sanitized.source_hash,
        training_hashes=sanitized.training_hashes,
        grammar_hash=ACTION_SCHEMA_GRAMMAR_HASH,
        program_space_hash=enumeration.program_space_hash,
        programs_enumerated=len(enumeration.programs),
        demonstration_executions=demonstration_executions,
        training_exact_programs=len(exact),
        admitted_exact_programs=len(admitted),
        test_executions=test_executions,
        test_executable_programs=test_executable_programs,
        behavior_classes=len(behaviors),
        execution_errors=execution_errors,
        enumeration_complete=enumeration.complete,
        truncation_reason=enumeration.truncation_reason,
        provisional_admitted=allow_provisional,
    )
    return ActionSchemaCompilation(tuple(behaviors), receipt)


__all__ = [
    "ACTION_SCHEMA_GRAMMAR_HASH",
    "ACTION_SCHEMAS",
    "ACTION_SCHEMAS_BY_NAME",
    "ActionSchemaLimits",
    "ActionSchema",
    "ActionSchemaCompilation",
    "DEFAULT_ACTION_LIMITS",
    "PROVISIONAL",
    "RasterBehavior",
    "STABLE",
    "SchemaEnumeration",
    "SchemaProgram",
    "SchemaWorkReceipt",
    "TypedHole",
    "compile_action_schemas",
    "enumerate_action_schema_programs",
]
