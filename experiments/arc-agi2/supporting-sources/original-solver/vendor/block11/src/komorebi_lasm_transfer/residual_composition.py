"""Label-blind, bounded residual composition for PR-LASM Block 11.

The lane searches a deliberately small and complete two-stage grammar on tasks
whose *training* deltas are pure recolor or pure support addition.  Exact grids
remain authoritative.  After the first executable action, the residual packet
is recomputed from the exact intermediate rasters with root backgrounds frozen;
only certified monotone progress enters the second stage.

Programs contain only two immutable ``grid -> grid`` action records.  They
contain no task identifier, answer raster, expected-answer hash, or source
example.  Search and execution never inspect a test ``output`` field.

All resource caps are semantic completeness boundaries: if any cap is reached,
the lane discards every candidate and returns an explicit incomplete receipt.

Author: Komorebi P.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from komorebi_lasm_composition.model import (
    Grid,
    canonical_json,
    canonical_value,
    sha256_record,
    validate_grid,
)
from komorebi_lasm_composition.residual import (
    certify_transition,
    derive_residual_batch,
    infer_background,
    state_hash,
)
from komorebi_lasm_composition.stages import (
    ATOMIC_REGISTRY_HASH,
    _atomic_parameter_candidates,
    atomic_leaf,
    execute_leaf,
)
from komorebi_lasm_composition.task import sanitize_training_task
from komorebi_lasm_action.tools import TOOL_LANGUAGE_HASH, ToolProgram, execute_tool


SCHEMA_VERSION = 1
LANE_NAME = "residual_composition"
ROUTE_KINDS = frozenset({("recolor",), ("support_add",)})
FORBIDDEN_PROGRAM_KEYS = frozenset({
    "task_id",
    "task_ids",
    "target",
    "target_grid",
    "targets",
    "expected",
    "expected_grid",
    "expected_output",
    "answer",
    "answer_hash",
    "solutions",
    "test_output",
    "training_hashes",
    "output",
    "outputs",
    "prediction",
    "predictions",
    "label",
    "labels",
    "solution",
    "solutions",
    "source_task",
    "source_task_id",
})


def _grid(value: Any) -> Grid:
    return validate_grid(value)


def _forbidden_key(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_PROGRAM_KEYS:
                return normalized
            nested = _forbidden_key(item)
            if nested is not None:
                return nested
    elif isinstance(value, (list, tuple)):
        for item in value:
            nested = _forbidden_key(item)
            if nested is not None:
                return nested
    return None


@dataclass(frozen=True, slots=True)
class ResidualCompositionLimits:
    """Hard completeness limits for the finite two-stage grammar."""

    max_training_examples: int = 10
    max_test_examples: int = 10
    max_atomic_stages_per_state: int = 512
    max_shape_transfer_stages_per_state: int = 384
    max_intermediate_behaviors: int = 256
    max_proposals: int = 32_768
    max_executor_calls: int = 131_072
    max_exact_programs: int = 1_024
    max_behavior_classes: int = 256
    max_total_cost: int = 24
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "max_training_examples",
            "max_test_examples",
            "max_atomic_stages_per_state",
            "max_shape_transfer_stages_per_state",
            "max_intermediate_behaviors",
            "max_proposals",
            "max_executor_calls",
            "max_exact_programs",
            "max_behavior_classes",
            "max_total_cost",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_transfer.residual_composition_limits",
            "schema_version": self.schema_version,
            "max_training_examples": self.max_training_examples,
            "max_test_examples": self.max_test_examples,
            "max_atomic_stages_per_state": self.max_atomic_stages_per_state,
            "max_shape_transfer_stages_per_state": self.max_shape_transfer_stages_per_state,
            "max_intermediate_behaviors": self.max_intermediate_behaviors,
            "max_proposals": self.max_proposals,
            "max_executor_calls": self.max_executor_calls,
            "max_exact_programs": self.max_exact_programs,
            "max_behavior_classes": self.max_behavior_classes,
            "max_total_cost": self.max_total_cost,
        }


DEFAULT_LIMITS = ResidualCompositionLimits()
SHAPE_TRANSFER_ROLES = (
    "unique_foreground",
    "rarest_foreground",
    "most_foreground",
) + tuple(f"literal:{color}" for color in range(10))
SHAPE_TRANSFER_BACKGROUND_ROLES = ("background", "corner", "zero")
SHAPE_TRANSFER_CONNECTIVITIES = (4, 8)
SHAPE_TRANSFER_MONOCHROME = (True, False)
SHAPE_TRANSFER_MODES = ("exact", "d4")
RESIDUAL_COMPOSITION_GRAMMAR_HASH = sha256_record({
    "schema": "komorebi.lasm_transfer.residual_composition_grammar",
    "schema_version": SCHEMA_VERSION,
    "composition_depth": 2,
    "route_kinds": [list(value) for value in sorted(ROUTE_KINDS)],
    "stage_namespaces": ["block9_atomic", "block10_semantic"],
    "progress_certificates": ["residual_subset", "shape_correction"],
    "atomic_registry_hash": ATOMIC_REGISTRY_HASH,
    "tool_language_hash": TOOL_LANGUAGE_HASH,
    "shape_transfer_domain": {
        "roles": list(SHAPE_TRANSFER_ROLES),
        "background_roles": list(SHAPE_TRANSFER_BACKGROUND_ROLES),
        "connectivities": list(SHAPE_TRANSFER_CONNECTIVITIES),
        "monochrome_components": list(SHAPE_TRANSFER_MONOCHROME),
        "shape_modes": list(SHAPE_TRANSFER_MODES),
        "selector": "color_components",
        "relation": "none",
        "geometry": "shape_color_transfer",
        "effect": "paint_source_color",
        "closure": "once",
        "cost": 7,
    },
    "limits": DEFAULT_LIMITS.to_record(),
})


@dataclass(frozen=True, slots=True)
class TypedResidualStage:
    """One immutable target-free ``grid -> grid`` action."""

    namespace: str
    family: str
    program_json: str
    cost: int
    semantic_id: str
    input_type: str = "grid"
    output_type: str = "grid"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.namespace not in {"block9_atomic", "block10_semantic"}:
            raise ValueError("unsupported residual-stage namespace")
        if not isinstance(self.family, str) or not self.family:
            raise ValueError("stage family must be nonempty")
        if self.input_type != "grid" or self.output_type != "grid":
            raise ValueError("residual stages must have type grid -> grid")
        if isinstance(self.cost, bool) or not isinstance(self.cost, int) or self.cost < 1:
            raise ValueError("stage cost must be a positive integer")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        try:
            record = json.loads(self.program_json)
        except (TypeError, ValueError) as error:
            raise ValueError("program_json must encode JSON") from error
        if not isinstance(record, dict) or canonical_json(record) != self.program_json:
            raise ValueError("program_json must encode a canonical object")
        forbidden = _forbidden_key(record)
        if forbidden is not None:
            raise ValueError(f"target-free stage contains forbidden key {forbidden!r}")
        if len(self.semantic_id) != 64 or any(
            character not in "0123456789abcdef" for character in self.semantic_id
        ):
            raise ValueError("semantic_id must be a lowercase SHA-256 digest")
        # Rehydrate immediately.  This authenticates the semantic digest and
        # exact parameter schema before a stage can enter a word.
        _rehydrate_stage(self)

    @property
    def program_record(self) -> Mapping[str, Any]:
        return MappingProxyType(json.loads(self.program_json))

    @property
    def stage_id(self) -> str:
        return sha256_record({
            "namespace": self.namespace,
            "family": self.family,
            "program": dict(self.program_record),
            "cost": self.cost,
            "semantic_id": self.semantic_id,
            "input_type": self.input_type,
            "output_type": self.output_type,
        })

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_transfer.typed_residual_stage",
            "schema_version": self.schema_version,
            "namespace": self.namespace,
            "family": self.family,
            "program": dict(self.program_record),
            "program_json": self.program_json,
            "cost": self.cost,
            "semantic_id": self.semantic_id,
            "stage_id": self.stage_id,
            "input_type": self.input_type,
            "output_type": self.output_type,
        }


def _rehydrate_stage(stage: TypedResidualStage) -> Any:
    record = json.loads(stage.program_json)
    if stage.namespace == "block9_atomic":
        parameters = record.get("parameters")
        if not isinstance(parameters, Mapping):
            raise ValueError("atomic stage record lacks parameters")
        leaf = atomic_leaf(stage.family, parameters)
        if leaf.semantic_hash != stage.semantic_id:
            raise ValueError("atomic stage semantic digest disagrees")
        if leaf.cost != stage.cost:
            raise ValueError("atomic stage cost disagrees")
        if canonical_json(leaf.to_record()) != stage.program_json:
            raise ValueError("atomic stage record is not canonical and exact")
        return leaf
    if stage.namespace == "block10_semantic":
        tool = ToolProgram.from_record(record)
        if tool.geometry != stage.family or tool.tool_id != stage.semantic_id:
            raise ValueError("semantic stage identity disagrees")
        if tool.cost != stage.cost:
            raise ValueError("semantic stage cost disagrees")
        if canonical_json(tool.to_record()) != stage.program_json:
            raise ValueError("semantic stage record is not canonical and exact")
        return tool
    raise ValueError("unsupported residual-stage namespace")


def _execute_stage(stage: TypedResidualStage, grid: Any) -> Grid:
    program = _rehydrate_stage(stage)
    if stage.namespace == "block9_atomic":
        return _grid(execute_leaf(program, grid))
    return _grid(execute_tool(program, grid))


@dataclass(frozen=True, slots=True)
class ResidualCompositionProgram:
    """Exactly two immutable, target-free typed actions."""

    stages: tuple[TypedResidualStage, TypedResidualStage]
    route_kinds: tuple[str, ...]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "stages", tuple(self.stages))
        object.__setattr__(self, "route_kinds", tuple(self.route_kinds))
        if len(self.stages) != 2:
            raise ValueError("residual composition programs require exactly two stages")
        if self.route_kinds not in ROUTE_KINDS:
            raise ValueError("program route must be pure recolor or pure support-add")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        if any(stage.input_type != "grid" or stage.output_type != "grid" for stage in self.stages):
            raise ValueError("program stages must compose at grid type")

    @property
    def total_cost(self) -> int:
        return sum(stage.cost for stage in self.stages)

    @property
    def word_schema(self) -> tuple[str, str]:
        return tuple(
            f"{stage.namespace}:{stage.family}" for stage in self.stages
        )  # type: ignore[return-value]

    @property
    def program_id(self) -> str:
        return sha256_record({
            "stages": [stage.stage_id for stage in self.stages],
            "route_kinds": list(self.route_kinds),
        })

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_transfer.residual_composition_program",
            "schema_version": self.schema_version,
            "input_type": "grid",
            "output_type": "grid",
            "route_kinds": list(self.route_kinds),
            "word_schema": list(self.word_schema),
            "total_cost": self.total_cost,
            "stages": [stage.to_record() for stage in self.stages],
            "program_id": self.program_id,
        }
        forbidden = _forbidden_key(record)
        if forbidden is not None:
            raise ValueError(f"target-free program contains forbidden key {forbidden!r}")
        return record


def execute_residual_program(program: ResidualCompositionProgram, grid: Any) -> Grid:
    """Execute one frozen word without task, target, or corpus access."""

    if not isinstance(program, ResidualCompositionProgram):
        raise TypeError("program must be a ResidualCompositionProgram")
    current = _grid(grid)
    for stage in program.stages:
        current = _execute_stage(stage, current)
    return current


@dataclass(frozen=True, slots=True)
class ResidualBehavior:
    predictions: tuple[Grid, ...]
    representative: ResidualCompositionProgram
    equivalent_program_ids: tuple[str, ...]

    @property
    def behavior_hash(self) -> str:
        return sha256_record(self.predictions)

    def to_record(self) -> dict[str, Any]:
        return {
            "behavior_hash": self.behavior_hash,
            "predictions": canonical_value(self.predictions),
            "representative_program": self.representative.to_record(),
            "equivalent_program_ids": list(self.equivalent_program_ids),
            "equivalent_programs": len(self.equivalent_program_ids),
        }


@dataclass(frozen=True, slots=True)
class ResidualCompositionReceipt:
    route_eligible: bool
    enumeration_complete: bool
    truncation_reason: str
    root_packet_id: str
    route_kinds: tuple[str, ...]
    limits_id: str
    atomic_syntax_generated: int
    shape_syntax_generated: int
    states_expanded: int
    proposals_executed: int
    executor_calls: int
    execution_errors: int
    progress_rejections: int
    transitions_accepted: int
    packet_recomputations: int
    intermediate_behavior_classes: int
    intermediate_programs: int
    exact_programs: int
    reducible_programs: int
    training_replay_rejections: int
    test_execution_rejections: int
    behavior_classes: int
    schema_version: int = SCHEMA_VERSION

    @property
    def receipt_hash(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_transfer.residual_composition_receipt",
            "schema_version": self.schema_version,
            "route_eligible": self.route_eligible,
            "enumeration_complete": self.enumeration_complete,
            "truncation_reason": self.truncation_reason,
            "root_packet_id": self.root_packet_id,
            "route_kinds": list(self.route_kinds),
            "limits_id": self.limits_id,
            "atomic_syntax_generated": self.atomic_syntax_generated,
            "shape_syntax_generated": self.shape_syntax_generated,
            "states_expanded": self.states_expanded,
            "proposals_executed": self.proposals_executed,
            "executor_calls": self.executor_calls,
            "execution_errors": self.execution_errors,
            "progress_rejections": self.progress_rejections,
            "transitions_accepted": self.transitions_accepted,
            "packet_recomputations": self.packet_recomputations,
            "intermediate_behavior_classes": self.intermediate_behavior_classes,
            "intermediate_programs": self.intermediate_programs,
            "exact_programs": self.exact_programs,
            "reducible_programs": self.reducible_programs,
            "training_replay_rejections": self.training_replay_rejections,
            "test_execution_rejections": self.test_execution_rejections,
            "behavior_classes": self.behavior_classes,
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.identity_record, "receipt_hash": self.receipt_hash}


@dataclass(frozen=True, slots=True)
class ResidualCompositionResult:
    behaviors: tuple[ResidualBehavior, ...]
    receipt: ResidualCompositionReceipt

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
        return self.behaviors[0].predictions if len(self.behaviors) == 1 else None

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_transfer.residual_composition_result",
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "prediction": canonical_value(self.prediction),
            "behaviors": [behavior.to_record() for behavior in self.behaviors],
            "receipt": self.receipt.to_record(),
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass
class _MutableWork:
    atomic_syntax_generated: int = 0
    shape_syntax_generated: int = 0
    states_expanded: int = 0
    proposals_executed: int = 0
    executor_calls: int = 0
    execution_errors: int = 0
    progress_rejections: int = 0
    transitions_accepted: int = 0
    packet_recomputations: int = 0
    intermediate_behavior_classes: int = 0
    intermediate_programs: int = 0
    exact_programs: int = 0
    reducible_programs: int = 0
    training_replay_rejections: int = 0
    test_execution_rejections: int = 0
    behavior_classes: int = 0
    truncation_reason: str = ""

    def truncate(self, reason: str) -> None:
        if not self.truncation_reason:
            self.truncation_reason = reason


@dataclass(frozen=True, slots=True)
class _Intermediate:
    grids: tuple[Grid, ...]
    firsts: tuple[TypedResidualStage, ...]
    certificate_hash: str
    residual_packet_id: str
    residual_score: tuple[int, int, int, int]

    @property
    def representative(self) -> TypedResidualStage:
        return self.firsts[0]


def _stage_from_leaf(leaf: Any) -> TypedResidualStage:
    return TypedResidualStage(
        namespace="block9_atomic",
        family=leaf.family,
        program_json=canonical_json(leaf.to_record()),
        cost=int(leaf.cost),
        semantic_id=leaf.semantic_hash,
    )


def _stage_from_tool(tool: ToolProgram) -> TypedResidualStage:
    return TypedResidualStage(
        namespace="block10_semantic",
        family=tool.geometry,
        program_json=canonical_json(tool.to_record()),
        cost=int(tool.cost),
        semantic_id=tool.tool_id,
    )


def _atomic_stages(
    currents: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    packet: Any,
    limits: ResidualCompositionLimits,
    work: _MutableWork,
) -> tuple[TypedResidualStage, ...]:
    unique: dict[tuple[str, str], Any] = {}
    for family, parameters in _atomic_parameter_candidates(currents, targets, packet):
        try:
            leaf = atomic_leaf(family, parameters)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        unique[(leaf.family, leaf.parameters_json)] = leaf
    work.atomic_syntax_generated += len(unique)
    if len(unique) > limits.max_atomic_stages_per_state:
        work.truncate("max_atomic_stages_per_state")
        return ()
    return tuple(
        _stage_from_leaf(leaf)
        for leaf in sorted(
            unique.values(),
            key=lambda item: (
                item.cost,
                item.macro_schema,
                item.family,
                item.parameters_json,
                item.semantic_hash,
            ),
        )
    )


def _shape_transfer_stages(
    limits: ResidualCompositionLimits,
    work: _MutableWork,
) -> tuple[TypedResidualStage, ...]:
    """Enumerate the complete compact color/shape-transfer subgrammar."""

    unique: dict[str, ToolProgram] = {}
    for background_role in SHAPE_TRANSFER_BACKGROUND_ROLES:
        for connectivity in SHAPE_TRANSFER_CONNECTIVITIES:
            for monochrome in SHAPE_TRANSFER_MONOCHROME:
                for selector_role in SHAPE_TRANSFER_ROLES:
                    for shape_mode in SHAPE_TRANSFER_MODES:
                        parameters = {
                            "background_role": background_role,
                            "connectivity": connectivity,
                            "monochrome_components": monochrome,
                            "selector_color_role": selector_role,
                            "paint_role": "source",
                            "background_only": False,
                            "include_sources": True,
                            "directions": [],
                            "offset": [0, 0],
                            "stamp_offsets": [],
                            "max_steps": 30,
                            "shape_mode": shape_mode,
                        }
                        tool = ToolProgram.from_parameters(
                            selector="color_components",
                            relation="none",
                            geometry="shape_color_transfer",
                            effect="paint_source_color",
                            closure="once",
                            parameters=parameters,
                            cost=7,
                        )
                        unique[tool.tool_id] = tool
    work.shape_syntax_generated += len(unique)
    if len(unique) > limits.max_shape_transfer_stages_per_state:
        work.truncate("max_shape_transfer_stages_per_state")
        return ()
    return tuple(
        _stage_from_tool(tool)
        for tool in sorted(unique.values(), key=lambda item: (item.cost, item.tool_id))
    )


def _stages_for_state(
    currents: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    packet: Any,
    limits: ResidualCompositionLimits,
    work: _MutableWork,
) -> tuple[TypedResidualStage, ...]:
    atomic = _atomic_stages(currents, targets, packet, limits, work)
    if work.truncation_reason:
        return ()
    semantic = _shape_transfer_stages(limits, work)
    if work.truncation_reason:
        return ()
    return tuple(sorted(
        atomic + semantic,
        key=lambda stage: (
            stage.cost,
            stage.namespace,
            stage.family,
            stage.semantic_id,
        ),
    ))


def _can_execute(
    work: _MutableWork,
    limits: ResidualCompositionLimits,
    calls: int,
) -> bool:
    if work.proposals_executed + 1 > limits.max_proposals:
        work.truncate("max_proposals")
        return False
    if work.executor_calls + calls > limits.max_executor_calls:
        work.truncate("max_executor_calls")
        return False
    return True


def _execute_batch(
    stage: TypedResidualStage,
    grids: tuple[Grid, ...],
    limits: ResidualCompositionLimits,
    work: _MutableWork,
) -> tuple[Grid, ...] | None:
    if not _can_execute(work, limits, len(grids)):
        return None
    work.proposals_executed += 1
    outputs: list[Grid] = []
    for grid in grids:
        work.executor_calls += 1
        try:
            outputs.append(_execute_stage(stage, grid))
        except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
            work.execution_errors += 1
            return None
    return tuple(outputs)


def _packet_score(packet: Any) -> tuple[int, int, int, int]:
    return tuple(
        sum(example.measure[index] for example in packet.examples)
        for index in range(4)
    )  # type: ignore[return-value]


def residual_composition_route(task: Mapping[str, Any]) -> bool:
    """Training-only task-ID-independent route predicate."""

    safe = sanitize_training_task(task)
    inputs = tuple(_grid(grid) for grid in safe.training_inputs)
    targets = tuple(_grid(grid) for grid in safe.training_outputs)
    backgrounds = tuple(infer_background(grid) for grid in inputs)
    packet = derive_residual_batch(inputs, targets, root_backgrounds=backgrounds)
    return tuple(packet.union_kinds) in ROUTE_KINDS


def _receipt(
    *,
    eligible: bool,
    packet: Any,
    limits: ResidualCompositionLimits,
    work: _MutableWork,
) -> ResidualCompositionReceipt:
    return ResidualCompositionReceipt(
        route_eligible=eligible,
        enumeration_complete=not bool(work.truncation_reason),
        truncation_reason=work.truncation_reason,
        root_packet_id=packet.aggregate_packet_id,
        route_kinds=tuple(packet.union_kinds),
        limits_id=sha256_record(limits.to_record()),
        atomic_syntax_generated=work.atomic_syntax_generated,
        shape_syntax_generated=work.shape_syntax_generated,
        states_expanded=work.states_expanded,
        proposals_executed=work.proposals_executed,
        executor_calls=work.executor_calls,
        execution_errors=work.execution_errors,
        progress_rejections=work.progress_rejections,
        transitions_accepted=work.transitions_accepted,
        packet_recomputations=work.packet_recomputations,
        intermediate_behavior_classes=work.intermediate_behavior_classes,
        intermediate_programs=work.intermediate_programs,
        exact_programs=work.exact_programs,
        reducible_programs=work.reducible_programs,
        training_replay_rejections=work.training_replay_rejections,
        test_execution_rejections=work.test_execution_rejections,
        behavior_classes=work.behavior_classes,
    )


def compile_residual_composition(
    task: Mapping[str, Any],
    *,
    limits: ResidualCompositionLimits = DEFAULT_LIMITS,
) -> ResidualCompositionResult:
    """Compile, exact-replay, freeze, execute, and behavior-quotient one task."""

    if not isinstance(limits, ResidualCompositionLimits):
        raise TypeError("limits must be a ResidualCompositionLimits record")
    safe = sanitize_training_task(task)
    inputs = tuple(_grid(grid) for grid in safe.training_inputs)
    targets = tuple(_grid(grid) for grid in safe.training_outputs)
    tests = tuple(_grid(grid) for grid in safe.test_inputs)
    input_limit = ""
    if len(inputs) > limits.max_training_examples:
        input_limit = "training_example_limit"
    elif len(tests) > limits.max_test_examples:
        input_limit = "test_example_limit"
    if input_limit:
        work = _MutableWork(truncation_reason=input_limit)
        receipt = ResidualCompositionReceipt(
            route_eligible=False,
            enumeration_complete=False,
            truncation_reason=input_limit,
            root_packet_id=sha256_record({
                "source_hash": safe.source_hash,
                "limit": input_limit,
            }),
            route_kinds=(),
            limits_id=sha256_record(limits.to_record()),
            atomic_syntax_generated=0,
            shape_syntax_generated=0,
            states_expanded=0,
            proposals_executed=0,
            executor_calls=0,
            execution_errors=0,
            progress_rejections=0,
            transitions_accepted=0,
            packet_recomputations=0,
            intermediate_behavior_classes=0,
            intermediate_programs=0,
            exact_programs=0,
            reducible_programs=0,
            training_replay_rejections=0,
            test_execution_rejections=0,
            behavior_classes=0,
        )
        return ResidualCompositionResult(behaviors=(), receipt=receipt)
    backgrounds = tuple(infer_background(grid) for grid in inputs)
    root_packet = derive_residual_batch(inputs, targets, root_backgrounds=backgrounds)
    work = _MutableWork(packet_recomputations=1)
    eligible = tuple(root_packet.union_kinds) in ROUTE_KINDS
    if not eligible:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=False, packet=root_packet, limits=limits, work=work),
        )

    root_stages = _stages_for_state(inputs, targets, root_packet, limits, work)
    if work.truncation_reason:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )

    root_hash = state_hash(inputs)
    intermediates: dict[str, _Intermediate] = {}
    work.states_expanded = 1
    for stage in root_stages:
        if stage.cost > limits.max_total_cost:
            work.progress_rejections += 1
            continue
        after = _execute_batch(stage, inputs, limits, work)
        if work.truncation_reason:
            break
        if after is None:
            continue
        certificate = certify_transition(
            inputs,
            after,
            targets,
            mode="residual_subset",
            root_backgrounds=backgrounds,
            visited_state_hashes=(root_hash,),
        )
        if certificate is None:
            certificate = certify_transition(
                inputs,
                after,
                targets,
                mode="shape_correction",
                root_backgrounds=backgrounds,
                visited_state_hashes=(root_hash,),
            )
        if certificate is None:
            work.progress_rejections += 1
            continue
        after_packet = derive_residual_batch(
            after, targets, root_backgrounds=backgrounds,
        )
        work.packet_recomputations += 1
        # A one-stage exact program is outside this lane and cannot seed a
        # reducible two-stage word.
        if after_packet.exact:
            continue
        work.transitions_accepted += 1
        value = _Intermediate(
            grids=after,
            firsts=(stage,),
            certificate_hash=certificate.certificate_hash,
            residual_packet_id=after_packet.aggregate_packet_id,
            residual_score=_packet_score(after_packet),
        )
        key = state_hash(after)
        prior = intermediates.get(key)
        if prior is None:
            intermediates[key] = value
        else:
            firsts = {
                item.stage_id: item for item in (*prior.firsts, stage)
            }
            intermediates[key] = _Intermediate(
                grids=prior.grids,
                firsts=tuple(sorted(
                    firsts.values(), key=lambda item: (item.cost, item.stage_id),
                )),
                certificate_hash=prior.certificate_hash,
                residual_packet_id=prior.residual_packet_id,
                residual_score=prior.residual_score,
            )

    if work.truncation_reason:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )
    work.intermediate_behavior_classes = len(intermediates)
    work.intermediate_programs = sum(len(value.firsts) for value in intermediates.values())
    if len(intermediates) > limits.max_intermediate_behaviors:
        work.truncate("max_intermediate_behaviors")
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )

    exact: dict[str, ResidualCompositionProgram] = {}
    for intermediate in sorted(
        intermediates.values(),
        key=lambda item: (
            item.residual_score,
            item.representative.cost,
            item.representative.stage_id,
            state_hash(item.grids),
        ),
    ):
        work.states_expanded += 1
        packet = derive_residual_batch(
            intermediate.grids, targets, root_backgrounds=backgrounds,
        )
        work.packet_recomputations += 1
        second_stages = _stages_for_state(
            intermediate.grids, targets, packet, limits, work,
        )
        if work.truncation_reason:
            break
        for second in second_stages:
            firsts = tuple(
                first for first in intermediate.firsts
                if first.cost + second.cost <= limits.max_total_cost
            )
            work.progress_rejections += len(intermediate.firsts) - len(firsts)
            if not firsts:
                continue
            final = _execute_batch(second, intermediate.grids, limits, work)
            if work.truncation_reason:
                break
            if final is None or final != targets:
                continue
            # Exact irreducibility check: the second action alone must not be a
            # complete root solution.
            second_alone = _execute_batch(second, inputs, limits, work)
            if work.truncation_reason:
                break
            if second_alone == targets:
                work.reducible_programs += 1
                continue
            for first in firsts:
                program = ResidualCompositionProgram(
                    stages=(first, second),
                    route_kinds=tuple(root_packet.union_kinds),
                )
                exact.setdefault(program.program_id, program)
                if len(exact) > limits.max_exact_programs:
                    work.truncate("max_exact_programs")
                    break
            if work.truncation_reason:
                break
        if work.truncation_reason:
            break

    if work.truncation_reason:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )
    work.exact_programs = len(exact)

    replayed: list[ResidualCompositionProgram] = []
    for program in sorted(
        exact.values(), key=lambda item: (item.total_cost, item.word_schema, item.program_id),
    ):
        outputs: list[Grid] = []
        failed = False
        for grid in inputs:
            if work.executor_calls + 2 > limits.max_executor_calls:
                work.truncate("max_executor_calls")
                failed = True
                break
            try:
                outputs.append(execute_residual_program(program, grid))
                work.executor_calls += 2
            except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
                work.executor_calls += 2
                work.execution_errors += 1
                failed = True
                break
        if failed:
            work.training_replay_rejections += 1
            if work.truncation_reason:
                break
            continue
        if tuple(outputs) != targets:
            work.training_replay_rejections += 1
            continue
        replayed.append(program)

    if work.truncation_reason:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )

    quotient: dict[str, tuple[tuple[Grid, ...], list[ResidualCompositionProgram]]] = {}
    for program in replayed:
        outputs: list[Grid] = []
        failed = False
        for grid in tests:
            if work.executor_calls + 2 > limits.max_executor_calls:
                work.truncate("max_executor_calls")
                failed = True
                break
            try:
                outputs.append(execute_residual_program(program, grid))
                work.executor_calls += 2
            except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
                work.executor_calls += 2
                work.execution_errors += 1
                failed = True
                break
        if failed:
            work.test_execution_rejections += 1
            if work.truncation_reason:
                break
            continue
        frozen_outputs = tuple(outputs)
        behavior_hash = sha256_record(frozen_outputs)
        if behavior_hash not in quotient:
            quotient[behavior_hash] = (frozen_outputs, [])
        quotient[behavior_hash][1].append(program)

    if work.truncation_reason:
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )
    if len(quotient) > limits.max_behavior_classes:
        work.truncate("max_behavior_classes")
        return ResidualCompositionResult(
            behaviors=(),
            receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
        )

    behaviors: list[ResidualBehavior] = []
    for behavior_hash in sorted(quotient):
        outputs, programs = quotient[behavior_hash]
        ordered = sorted(
            programs, key=lambda item: (item.total_cost, item.word_schema, item.program_id),
        )
        behaviors.append(ResidualBehavior(
            predictions=outputs,
            representative=ordered[0],
            equivalent_program_ids=tuple(sorted(item.program_id for item in programs)),
        ))
    work.behavior_classes = len(behaviors)
    return ResidualCompositionResult(
        behaviors=tuple(behaviors),
        receipt=_receipt(eligible=True, packet=root_packet, limits=limits, work=work),
    )


def compile_residual_composition_lane(
    task: Mapping[str, Any],
) -> tuple[Any, ...]:
    """Adapt complete residual behaviors to the unified external-lane API."""

    # Local import avoids a module cycle: ``compiler`` owns the adapter type and
    # may itself import this function when wiring default external lanes.
    from .compiler import ExternalLaneBehavior

    result = compile_residual_composition(task)
    if not result.receipt.enumeration_complete:
        return ()
    return tuple(
        ExternalLaneBehavior(
            lane=LANE_NAME,
            predictions=behavior.predictions,
            mechanism={
                "word_schema": list(behavior.representative.word_schema),
                "representative_program": behavior.representative.to_record(),
                "equivalent_program_ids": list(behavior.equivalent_program_ids),
                "equivalent_programs": len(behavior.equivalent_program_ids),
                "receipt_hash": result.receipt.receipt_hash,
                "enumeration_complete": True,
            },
        )
        for behavior in result.behaviors
    )


__all__ = [
    "DEFAULT_LIMITS",
    "LANE_NAME",
    "RESIDUAL_COMPOSITION_GRAMMAR_HASH",
    "ResidualBehavior",
    "ResidualCompositionLimits",
    "ResidualCompositionProgram",
    "ResidualCompositionReceipt",
    "ResidualCompositionResult",
    "TypedResidualStage",
    "compile_residual_composition",
    "compile_residual_composition_lane",
    "execute_residual_program",
    "residual_composition_route",
]
