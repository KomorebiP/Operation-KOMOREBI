"""Transparent Program IR v2 lowering for recursive Block 9 compositions.

The important boundary in this module is that a :class:`CompositeProgram` is
*not* hidden behind a single executor call.  Every expanded leaf becomes one
``CallNode`` and the calls are nested in execution order.  Consequently the
canonical Program IR record exposes the composition tree to validation,
behaviour quotienting, and later anti-unification.

Execution is deliberately redundant.  Every prefix is evaluated once through
the direct Block 9 stage API and once from the original input through its
nested Program IR prefix.  A disagreement fails closed.  The reference
semantics for the composition-critical D4, crop, outer-U, and spiral leaves are
implemented locally rather than calling the direct stage dispatcher; this
makes the parity check capable of detecting accidental or monkeypatched direct
runtime changes.

This is a trusted diagnostic/lowering module, not the provenance-security
boundary. Program IR intentionally records executable semantics rather than
runtime-bank provenance. Untrusted programs must enter through
``compiler.execute_program``, which verifies the supplied Block 6, Block 8,
and Block 9 banks before calling these helpers.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from numbers import Integral
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from komorebi_lasm_compiler.ir_bridge import compiler_registry
from komorebi_lasm_ir import (
    ArcRuntimeAdapter,
    CallNode,
    ExecutionLimits,
    ExecutionTrace,
    InputNode,
    InputSpec,
    Interpreter,
    LiteralNode,
    OperatorDefinition,
    OperatorRegistry,
    Program,
    ValueType,
    standard_arc_registry,
)
from komorebi_lasm_synthesis.ir_bridge import synthesis_registry

from .model import (
    CompositeProgram,
    Grid,
    LeafInvocation,
    canonical_json,
    sha256_record,
    validate_grid,
)


ATOMIC_OPERATOR = "block9.execute_atomic_leaf"
BLOCK6_OPERATOR = "block6.execute_compiled_program"
BLOCK8_OPERATOR = "block8.execute_synthesized_macro"


class RegistryConflictError(ValueError):
    """Raised when inherited registries assign one name two signatures."""


class RegistryContractError(ValueError):
    """Raised when a composite was compiled against another registry."""


class IRParityError(RuntimeError):
    """Raised when direct and Program IR execution disagree at a prefix."""

    def __init__(
        self,
        prefix_index: int,
        leaf: LeafInvocation,
        direct_output: Grid,
        ir_output: Grid,
    ) -> None:
        self.prefix_index = int(prefix_index)
        self.leaf = leaf
        self.direct_output = direct_output
        self.ir_output = ir_output
        super().__init__(
            "Program IR parity failed after leaf "
            f"{self.prefix_index} ({leaf.namespace}:{leaf.family}); "
            f"direct={sha256_record(direct_output)}, "
            f"ir={sha256_record(ir_output)}"
        )


@dataclass(frozen=True, slots=True)
class PrefixExecution:
    """Audit evidence for one direct/IR prefix agreement."""

    prefix_index: int
    leaf_semantic_hash: str
    direct_output: Grid
    ir_output: Grid
    ir_program_hash: str
    registry_contract_hash: str
    trace: ExecutionTrace

    @property
    def output_hash(self) -> str:
        return sha256_record(self.ir_output)

    def to_record(self) -> dict[str, Any]:
        return {
            "prefix_index": self.prefix_index,
            "leaf_semantic_hash": self.leaf_semantic_hash,
            "direct_output_hash": sha256_record(self.direct_output),
            "ir_output_hash": sha256_record(self.ir_output),
            "ir_program_hash": self.ir_program_hash,
            "registry_contract_hash": self.registry_contract_hash,
            "trace": self.trace.to_record(),
        }


class StrictArcAdapter(ArcRuntimeAdapter):
    """ARC adapter that validates every grid before any integer coercion.

    Block 5's adapter correctly bounds NumPy results, but its generic result
    hook intentionally leaves tuple/list grids alone.  Recursive composition
    passes such values between independent packages, so this stricter adapter
    recognizes all three supported grid containers and enforces the ARC
    30-by-30, 900-cell, integer-category contract at each leaf boundary.
    Boolean ndarrays are masks rather than categorical grids and remain under
    the inherited mask path.
    """

    @staticmethod
    def _grid_candidate(value: object) -> bool:
        if isinstance(value, np.ndarray):
            return value.ndim == 2 and value.dtype.kind != "b"
        if isinstance(value, (str, bytes, bytearray, Mapping)):
            return False
        if not isinstance(value, (tuple, list)) or not value:
            return False
        # A tuple of Cells, Objects, or other packet values is a collection,
        # not a grid.  A grid necessarily has row-like first-level members.
        if not all(isinstance(row, (tuple, list, np.ndarray)) for row in value):
            return False
        # GRID_SET values are three-dimensional nested tuples.  Do not mistake
        # them for a malformed two-dimensional grid merely because their first
        # level also happens to be sequence-valued.
        for row in value:
            try:
                cells = list(row)
            except TypeError:
                return False
            if any(
                isinstance(cell, (tuple, list, np.ndarray, Mapping))
                for cell in cells
            ):
                return False
        return True

    def validate_result(self, value: object, limits: ExecutionLimits) -> object:
        if self._grid_candidate(value):
            grid = validate_grid(value)
            if len(grid) * len(grid[0]) > min(900, limits.maximum_grid_cells):
                raise ValueError("grid exceeds the configured 900-cell boundary")
            return grid
        return super().validate_result(value, limits)


def _signature(definition: OperatorDefinition) -> str:
    return json.dumps(
        definition.signature_record(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _merge_registry_definitions(
    registries: Iterable[OperatorRegistry],
    extensions: Iterable[OperatorDefinition] = (),
) -> tuple[OperatorDefinition, ...]:
    """Merge registries while proving duplicate names have one signature."""

    by_name: dict[str, OperatorDefinition] = {}
    signatures: dict[str, str] = {}
    for definition in (
        item
        for registry in registries
        for item in registry.definitions
    ):
        signature = _signature(definition)
        previous = signatures.get(definition.name)
        if previous is not None and previous != signature:
            raise RegistryConflictError(
                f"operator {definition.name!r} has conflicting inherited signatures"
            )
        signatures.setdefault(definition.name, signature)
        by_name.setdefault(definition.name, definition)
    for definition in extensions:
        signature = _signature(definition)
        previous = signatures.get(definition.name)
        if previous is not None:
            if previous != signature:
                raise RegistryConflictError(
                    f"operator {definition.name!r} conflicts with an inherited signature"
                )
            continue
        signatures[definition.name] = signature
        by_name[definition.name] = definition
    return tuple(by_name[name] for name in sorted(by_name))


def _decode_atomic_specification(specification: str) -> tuple[str, str, dict[str, Any]]:
    if not isinstance(specification, str):
        raise TypeError("atomic leaf specification must be canonical JSON text")
    try:
        record = json.loads(specification)
    except json.JSONDecodeError as error:
        raise ValueError("atomic leaf specification is not valid JSON") from error
    if not isinstance(record, dict) or set(record) != {
        "family", "macro_schema", "parameters"
    }:
        raise ValueError(
            "atomic leaf specification must contain exactly family, macro_schema, and parameters"
        )
    if canonical_json(record) != specification:
        raise ValueError("atomic leaf specification must use canonical JSON encoding")
    family = record["family"]
    macro_schema = record["macro_schema"]
    parameters = record["parameters"]
    if not isinstance(family, str) or not family or family != family.strip():
        raise ValueError("atomic family must be a nonempty trimmed string")
    if not isinstance(macro_schema, str) or not macro_schema or macro_schema != macro_schema.strip():
        raise ValueError("atomic macro_schema must be a nonempty trimmed string")
    if not isinstance(parameters, dict):
        raise TypeError("atomic parameters must be a JSON object")
    return family, macro_schema, parameters


def _color(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer color")
    result = int(value)
    if not 0 <= result <= 9:
        raise ValueError(f"{label} must lie in 0..9")
    return result


def _d4_reference(grid: Grid, transform: object) -> Grid:
    """Independent exact D4 action, with r90 counter-clockwise."""

    if not isinstance(transform, str):
        raise TypeError("D4 transform must be a string")

    def rotate90(value: Grid) -> Grid:
        height, width = len(value), len(value[0])
        return tuple(
            tuple(value[row][width - 1 - column] for row in range(height))
            for column in range(width)
        )

    if transform == "id":
        return grid
    if transform == "r90":
        return rotate90(grid)
    if transform == "r180":
        return rotate90(rotate90(grid))
    if transform == "r270":
        return rotate90(rotate90(rotate90(grid)))
    if transform in {"fliplr", "fh"}:
        return tuple(tuple(reversed(row)) for row in grid)
    if transform in {"flipud", "fv"}:
        return tuple(reversed(grid))
    if transform in {"transpose", "t"}:
        return tuple(
            tuple(grid[row][column] for row in range(len(grid)))
            for column in range(len(grid[0]))
        )
    if transform in {"anti_transpose", "at"}:
        transposed = _d4_reference(grid, "transpose")
        return _d4_reference(transposed, "r180")
    raise ValueError(f"unknown D4 transform {transform!r}")


def _crop_bbox_reference(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    if set(parameters) != {"background"}:
        raise ValueError("crop_bbox requires exactly the background parameter")
    background = _color(parameters.get("background"), "background")
    cells = [
        (row, column)
        for row, values in enumerate(grid)
        for column, value in enumerate(values)
        if value != background
    ]
    if not cells:
        raise ValueError("cannot crop an empty foreground")
    top = min(row for row, _ in cells)
    bottom = max(row for row, _ in cells)
    left = min(column for _, column in cells)
    right = max(column for _, column in cells)
    return tuple(tuple(row[left : right + 1]) for row in grid[top : bottom + 1])


def _outer_clockwise_u_reference(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    """Draw the open top/right/bottom prefix of a clockwise spiral."""

    if set(parameters) != {"background", "color"}:
        raise ValueError("outer_clockwise_u requires exactly background and color")
    background = _color(parameters.get("background"), "background")
    color = _color(parameters.get("color"), "color")
    if color == background:
        raise ValueError("spiral color must differ from its background")
    output = [list(row) for row in grid]
    height, width = len(output), len(output[0])
    if height != width or height < 4:
        raise ValueError("outer clockwise U requires a square of side at least four")
    if any(value != background for row in output for value in row):
        raise ValueError("outer clockwise U requires an exactly uniform background grid")
    for column in range(width):
        output[0][column] = color
    for row in range(1, height):
        output[row][width - 1] = color
    if height > 1:
        for column in range(width - 2, -1, -1):
            output[height - 1][column] = color
    return validate_grid(output)


def _continue_square_spiral_reference(grid: Grid, parameters: Mapping[str, Any]) -> Grid:
    """Continue a one-cell-separated clockwise square spiral inward.

    The input normally contains the outer clockwise U emitted by the preceding
    leaf.  Existing cells are preserved; each deeper turn is painted at an
    inset of two cells, with the previous left wall supplying the connector.
    """

    if set(parameters) != {"background", "color"}:
        raise ValueError("continue_square_spiral requires exactly background and color")
    background = _color(parameters.get("background"), "background")
    color = _color(parameters.get("color"), "color")
    if color == background:
        raise ValueError("spiral color must differ from its background")
    height, width = len(grid), len(grid[0])
    if height != width or height < 4:
        raise ValueError("square-spiral continuation requires a square of side at least four")

    expected = [[background for _ in range(width)] for _ in range(height)]
    for column in range(width):
        expected[0][column] = color
    for row in range(height):
        expected[row][width - 1] = color
    for column in range(width):
        expected[height - 1][column] = color
    if grid != validate_grid(expected):
        raise ValueError("square-spiral continuation requires the exact open-U prefix")

    output = [[background for _ in range(width)] for _ in range(height)]
    layer = 0
    while True:
        top = left = 2 * layer
        bottom = right = height - 1 - 2 * layer
        if top > bottom or left > right:
            break
        start = left if layer == 0 else left - 2
        for column in range(start, right + 1):
            output[top][column] = color
        for row in range(top, bottom + 1):
            output[row][right] = color
        for column in range(left, right + 1):
            output[bottom][column] = color
        for row in range(top + 2, bottom + 1):
            output[row][left] = color
        layer += 1
    if height % 2 == 0:
        output[height // 2][height // 2 - 1] = color
    if validate_grid(output) == grid:
        raise ValueError("square-spiral continuation must be nontrivial")
    return validate_grid(output)


def _execute_atomic_reference(grid: object, specification: str) -> Grid:
    source = validate_grid(grid)
    family, macro_schema, parameters = _decode_atomic_specification(specification)
    if family == "d4_transform":
        return validate_grid(_d4_reference(source, parameters.get("transform")))
    if family == "crop_bbox":
        return validate_grid(_crop_bbox_reference(source, parameters))
    if family == "outer_clockwise_u":
        return _outer_clockwise_u_reference(source, parameters)
    if family == "continue_square_spiral":
        return _continue_square_spiral_reference(source, parameters)
    if family == "dynamic_layout_from_scene":
        from .dynamic_layout import execute_dynamic_layout

        return validate_grid(execute_dynamic_layout(source, parameters))

    # The remaining atomic families have an explicitly opaque compatibility
    # route.  They can be moved above this boundary as independent reference
    # semantics are added; the four composition-critical families never pass
    # through the direct dispatcher.
    from . import stages

    leaf = LeafInvocation.from_parameters(
        namespace="atomic",
        family=family,
        macro_schema=macro_schema,
        parameters=parameters,
        source_macro_id="ir_reference_dispatch",
        cost=1,
    )
    return validate_grid(stages.execute_leaf(leaf, source))


@lru_cache(maxsize=1)
def composition_registry() -> OperatorRegistry:
    """Return the verified Block 5+6+8+9 Program IR registry."""

    from .stages import ATOMIC_REGISTRY_HASH

    atomic = OperatorDefinition(
        name=ATOMIC_OPERATOR,
        input_types=(ValueType.GRID, ValueType.SYMBOL),
        output_type=ValueType.GRID,
        function=_execute_atomic_reference,
        cost=10,
        pure=True,
        description=(
            "Execute one canonical Block 9 atomic grid leaf; composite control "
            "structure remains explicit in nested Program IR calls; "
            f"atomic_registry={ATOMIC_REGISTRY_HASH}."
        ),
    )
    definitions = _merge_registry_definitions(
        (standard_arc_registry(), compiler_registry(), synthesis_registry()),
        (atomic,),
    )
    registry = OperatorRegistry(definitions)
    # These inherited operators are part of the promised merged contract.  A
    # package missing either extension must fail during registry construction.
    required = {ATOMIC_OPERATOR, BLOCK6_OPERATOR, BLOCK8_OPERATOR}
    missing = required.difference(registry.names)
    if missing:
        raise RegistryConflictError(
            f"merged registry is missing required operators: {sorted(missing)}"
        )
    return registry


# The literal module-level value is the contract to which CompositeProgram
# records bind.  Execution compares the record's registry_hash against it.
REGISTRY_CONTRACT_HASH = composition_registry().contract_hash()
COMPOSITION_REGISTRY_CONTRACT_HASH = REGISTRY_CONTRACT_HASH


def registry_contract_hash() -> str:
    return REGISTRY_CONTRACT_HASH


def _assert_registry_binding(program: CompositeProgram) -> None:
    actual = composition_registry().contract_hash()
    if actual != REGISTRY_CONTRACT_HASH:
        raise RegistryContractError(
            "the live composition registry no longer matches its bound contract hash"
        )
    if program.registry_hash != REGISTRY_CONTRACT_HASH:
        raise RegistryContractError(
            "composite registry hash does not match the Block 9 Program IR contract: "
            f"program={program.registry_hash!r}, runtime={REGISTRY_CONTRACT_HASH!r}"
        )


def _leaf_specification(leaf: LeafInvocation) -> str:
    if leaf.namespace == "block6":
        return canonical_json(
            {"family": leaf.family, "parameters": leaf.parameters_record}
        )
    return canonical_json(
        {
            "family": leaf.family,
            "macro_schema": leaf.macro_schema,
            "parameters": leaf.parameters_record,
        }
    )


def lower_leaf(argument: Any, leaf: LeafInvocation) -> CallNode:
    """Lower one leaf around its already-lowered grid argument."""

    operators = {
        "atomic": ATOMIC_OPERATOR,
        "block6": BLOCK6_OPERATOR,
        "block8": BLOCK8_OPERATOR,
    }
    try:
        operator = operators[leaf.namespace]
    except KeyError as error:
        raise ValueError(f"unsupported leaf namespace {leaf.namespace!r}") from error
    return CallNode(
        operator,
        (
            argument,
            LiteralNode(ValueType.SYMBOL, _leaf_specification(leaf)),
        ),
        ValueType.GRID,
    )


def to_ir_program(
    program: CompositeProgram,
    *,
    prefix_length: int | None = None,
) -> Program:
    """Lower a preauthorized composite to genuinely nested Program IR calls.

    Source-macro identifiers and lifecycle status are derivation metadata and
    are deliberately absent from semantic Program IR. Callers handling
    untrusted records must authorize them through ``compiler.execute_program``
    before using this low-level representation.
    """

    if not isinstance(program, CompositeProgram):
        raise TypeError("to_ir_program requires a CompositeProgram")
    _assert_registry_binding(program)
    count = len(program.leaves) if prefix_length is None else prefix_length
    if isinstance(count, bool) or not isinstance(count, Integral):
        raise TypeError("prefix_length must be an integer")
    count = int(count)
    if not 1 <= count <= len(program.leaves):
        raise ValueError("prefix_length must select a nonempty composite prefix")
    root: Any = InputNode("grid", ValueType.GRID)
    for leaf in program.leaves[:count]:
        root = lower_leaf(root, leaf)
    result = Program(
        inputs=(InputSpec("grid", ValueType.GRID),),
        root=root,
    )
    result.validate(composition_registry())
    return result


lower_composite_program = to_ir_program


def prefix_ir_programs(program: CompositeProgram) -> tuple[Program, ...]:
    return tuple(
        to_ir_program(program, prefix_length=index)
        for index in range(1, len(program.leaves) + 1)
    )


def _interpreter() -> Interpreter:
    return Interpreter(
        composition_registry(),
        adapter=StrictArcAdapter(),
        limits=ExecutionLimits(
            maximum_evaluations=20_000,
            maximum_operator_cost=20_000,
            maximum_collection_items=4_096,
            maximum_fixed_point_steps=900,
            maximum_grid_cells=900,
        ),
    )


def execute_with_prefix_checks(
    program: CompositeProgram,
    grid: object,
) -> tuple[Grid, tuple[PrefixExecution, ...]]:
    """Execute and compare every direct/IR prefix, failing on first mismatch."""

    _assert_registry_binding(program)
    source = validate_grid(grid)
    direct_state = source
    evidence: list[PrefixExecution] = []

    # Delayed import avoids making stage compilation depend on registry
    # construction and, importantly, resolves monkeypatches at call time.
    from . import stages

    for index, (leaf, ir_program) in enumerate(
        zip(program.leaves, prefix_ir_programs(program)),
        start=1,
    ):
        direct_state = validate_grid(stages.execute_leaf(leaf, direct_state))
        result = _interpreter().execute(ir_program, {"grid": source})
        ir_state = validate_grid(result.value)
        if direct_state != ir_state:
            raise IRParityError(index, leaf, direct_state, ir_state)
        evidence.append(
            PrefixExecution(
                prefix_index=index,
                leaf_semantic_hash=leaf.semantic_hash,
                direct_output=direct_state,
                ir_output=ir_state,
                ir_program_hash=ir_program.content_hash(),
                registry_contract_hash=REGISTRY_CONTRACT_HASH,
                trace=result.trace,
            )
        )
    return evidence[-1].ir_output, tuple(evidence)


def execute_prefixes_via_ir(
    program: CompositeProgram,
    grid: object,
) -> tuple[Grid, ...]:
    """Return the checked IR value after every expanded leaf."""

    _, evidence = execute_with_prefix_checks(program, grid)
    return tuple(item.ir_output for item in evidence)


def execute_via_ir(program: CompositeProgram, grid: object) -> Grid:
    """Execute a composite under registry binding and per-prefix parity checks."""

    value, _ = execute_with_prefix_checks(program, grid)
    return value


def verify_prefix_parity(
    program: CompositeProgram,
    grids: Sequence[object],
) -> tuple[PrefixExecution, ...]:
    """Check every prefix on every supplied grid and return audit evidence."""

    if isinstance(grids, (str, bytes, bytearray)):
        raise TypeError("grids must be a sequence of grid values")
    records: list[PrefixExecution] = []
    for grid in grids:
        _, evidence = execute_with_prefix_checks(program, grid)
        records.extend(evidence)
    return tuple(records)


assert_prefix_parity = verify_prefix_parity


def bound_ir_record(program: CompositeProgram) -> dict[str, Any]:
    """Serialize the Program IR together with its immutable registry binding."""

    ir_program = to_ir_program(program)
    return {
        "schema": "komorebi.lasm_composition.bound_program_ir",
        "schema_version": 1,
        "registry_contract_hash": REGISTRY_CONTRACT_HASH,
        "program": ir_program.to_record(),
        "program_hash": ir_program.content_hash(),
    }


__all__ = [
    "ATOMIC_OPERATOR",
    "BLOCK6_OPERATOR",
    "BLOCK8_OPERATOR",
    "COMPOSITION_REGISTRY_CONTRACT_HASH",
    "IRParityError",
    "PrefixExecution",
    "REGISTRY_CONTRACT_HASH",
    "RegistryConflictError",
    "RegistryContractError",
    "StrictArcAdapter",
    "assert_prefix_parity",
    "bound_ir_record",
    "composition_registry",
    "execute_prefixes_via_ir",
    "execute_via_ir",
    "execute_with_prefix_checks",
    "lower_composite_program",
    "lower_leaf",
    "prefix_ir_programs",
    "registry_contract_hash",
    "to_ir_program",
    "verify_prefix_parity",
]
