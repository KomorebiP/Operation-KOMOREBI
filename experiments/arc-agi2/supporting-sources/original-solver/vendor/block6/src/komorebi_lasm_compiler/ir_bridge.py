"""Bridge compiled Block 6 programs into Program IR v2."""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from komorebi_lasm_ir import (
    CallNode, ExecutionLimits, InputNode, InputSpec, Interpreter, LiteralNode,
    OperatorDefinition, OperatorRegistry, Program, ValueType, standard_arc_registry,
)

from .common import freeze
from .execution import execute_spec
from .model import CompiledProgram, canonical_json


@lru_cache(maxsize=1)
def compiler_registry() -> OperatorRegistry:
    base = standard_arc_registry()
    extension = OperatorDefinition(
        name="block6.execute_compiled_program",
        input_types=(ValueType.GRID, ValueType.SYMBOL),
        output_type=ValueType.GRID,
        function=execute_spec,
        cost=8,
        pure=True,
        description="Execute one canonical Block 6 relational program specification.",
    )
    return OperatorRegistry((*base.definitions, extension))


def to_ir_program(program: CompiledProgram) -> Program:
    specification = canonical_json(program.signature_record)
    result = Program(
        inputs=(InputSpec("grid", ValueType.GRID),),
        root=CallNode(
            "block6.execute_compiled_program",
            (
                InputNode("grid", ValueType.GRID),
                LiteralNode(ValueType.SYMBOL, specification),
            ),
            ValueType.GRID,
        ),
    )
    result.validate(compiler_registry())
    return result


def execute_via_ir(program: CompiledProgram, grid: Any) -> tuple[tuple[int, ...], ...]:
    ir_program = to_ir_program(program)
    interpreter = Interpreter(
        compiler_registry(),
        limits=ExecutionLimits(
            maximum_evaluations=5_000,
            maximum_operator_cost=5_000,
            maximum_collection_items=2_048,
            maximum_fixed_point_steps=900,
            maximum_grid_cells=3_600,
        ),
    )
    result = interpreter.execute(ir_program, {"grid": freeze(grid)})
    return freeze(result.value)
