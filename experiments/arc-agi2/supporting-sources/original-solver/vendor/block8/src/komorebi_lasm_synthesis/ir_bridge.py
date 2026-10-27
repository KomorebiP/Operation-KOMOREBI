"""Program IR v2 bridge for synthesized Block 8 macro programs."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Mapping

from komorebi_lasm_ir import (
    CallNode, ExecutionLimits, InputNode, InputSpec, Interpreter, LiteralNode,
    OperatorDefinition, OperatorRegistry, Program, ValueType, standard_arc_registry,
)
from komorebi_lasm_compiler.common import freeze
from komorebi_lasm_compiler.model import canonical_json

from .families import execute_family
from .model import SynthesizedProgram


def execute_spec(grid: Any, specification: str) -> tuple[tuple[int, ...], ...]:
    record = json.loads(str(specification))
    if not isinstance(record, Mapping):
        raise TypeError("macro specification must decode to a mapping")
    return execute_family(str(record["family"]), grid, dict(record.get("parameters", {})))


@lru_cache(maxsize=1)
def synthesis_registry() -> OperatorRegistry:
    base = standard_arc_registry()
    extension = OperatorDefinition(
        name="block8.execute_synthesized_macro",
        input_types=(ValueType.GRID, ValueType.SYMBOL),
        output_type=ValueType.GRID,
        function=execute_spec,
        cost=9,
        pure=True,
        description="Execute one canonical obstruction-guided macro specification.",
    )
    return OperatorRegistry((*base.definitions, extension))


def to_ir_program(program: SynthesizedProgram) -> Program:
    specification = canonical_json(program.signature_record)
    result = Program(
        inputs=(InputSpec("grid", ValueType.GRID),),
        root=CallNode(
            "block8.execute_synthesized_macro",
            (InputNode("grid", ValueType.GRID), LiteralNode(ValueType.SYMBOL, specification)),
            ValueType.GRID,
        ),
    )
    result.validate(synthesis_registry())
    return result


def execute_via_ir(program: SynthesizedProgram, grid: Any) -> tuple[tuple[int, ...], ...]:
    interpreter = Interpreter(
        synthesis_registry(),
        limits=ExecutionLimits(
            maximum_evaluations=8_000,
            maximum_operator_cost=8_000,
            maximum_collection_items=4_096,
            maximum_fixed_point_steps=1_000,
            maximum_grid_cells=3_600,
        ),
    )
    result = interpreter.execute(to_ir_program(program), {"grid": freeze(grid)})
    return freeze(result.value)


__all__ = ["execute_spec", "execute_via_ir", "synthesis_registry", "to_ir_program"]
