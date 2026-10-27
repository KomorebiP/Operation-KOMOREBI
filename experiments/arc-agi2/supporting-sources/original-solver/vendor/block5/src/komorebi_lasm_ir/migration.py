"""Adapters from the existing ARC typed sequence AST into Program IR v2."""

from __future__ import annotations

from typing import Iterable

from .nodes import CallNode, InputNode
from .program import InputSpec, Program
from .registry import OperatorDefinition, OperatorRegistry
from .types import ValueType


def _v1_type(value: object) -> ValueType:
    text = str(getattr(value, "value", value))
    if text == "grid":
        return ValueType.GRID
    if text == "mask":
        return ValueType.MASK
    raise TypeError(f"unsupported v1 value type {text!r}")


def migrate_v1_ast(v1_program: object, *, input_name: str = "input") -> Program:
    """Convert a v1 identity/call/sequence tree into nested v2 calls.

    The adapter imports no private runtime state.  It reads the public node
    fields and preserves each declared primitive signature.
    """

    root = getattr(v1_program, "root", None)
    if root is None:
        raise TypeError("v1 program has no root node")
    input_type = _v1_type(getattr(root, "input_type"))
    current = InputNode(input_name, input_type)

    def apply_node(node: object, value: object) -> object:
        class_name = type(node).__name__
        if class_name == "IdentityNode":
            if _v1_type(getattr(node, "value_type")) != value.output_type:
                raise TypeError("v1 identity type does not match its input")
            return value
        if class_name == "CallNode":
            expected_input = _v1_type(getattr(node, "input_type"))
            output_type = _v1_type(getattr(node, "output_type"))
            if value.output_type != expected_input:
                raise TypeError("v1 call sequence has inconsistent types")
            return CallNode(str(getattr(node, "primitive")), (value,), output_type)
        if class_name == "SequenceNode":
            output = value
            for step in tuple(getattr(node, "steps")):
                output = apply_node(step, output)
            return output
        raise TypeError(f"unsupported v1 node {class_name!r}")

    converted = apply_node(root, current)
    return Program((InputSpec(input_name, input_type),), converted)


def registry_from_v1_definitions(definitions: Iterable[object]) -> OperatorRegistry:
    migrated = []
    for definition in definitions:
        migrated.append(
            OperatorDefinition(
                name=str(getattr(definition, "name")),
                input_types=(_v1_type(getattr(definition, "input_type")),),
                output_type=_v1_type(getattr(definition, "output_type")),
                function=getattr(definition, "function"),
                description="migrated v1 primitive",
            )
        )
    return OperatorRegistry(migrated)


__all__ = ["migrate_v1_ast", "registry_from_v1_definitions"]
