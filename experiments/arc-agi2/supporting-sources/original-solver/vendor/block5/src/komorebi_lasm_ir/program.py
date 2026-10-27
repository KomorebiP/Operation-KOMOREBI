"""Versioned programs, static typing, alpha normalization, and typed holes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .nodes import (
    AllNode,
    AnyNode,
    ArgExtremeNode,
    CallNode,
    CartesianMapNode,
    CountNode,
    CaseBranch,
    CaseNode,
    Expression,
    FilterNode,
    FoldNode,
    HoleNode,
    IfNode,
    InputNode,
    LetNode,
    LiteralNode,
    MapNode,
    PackNode,
    RenderNode,
    RepeatUntilStableNode,
    SelectNode,
    SortNode,
    TileNode,
    VariableNode,
    node_from_record,
    node_to_record,
)
from .registry import OperatorRegistry
from .types import ValueType, element_type, is_collection


IR_SCHEMA = "komorebi.lasm_program_ir"
IR_SCHEMA_VERSION = 2


class ProgramValidationError(ValueError):
    """Raised when a serialized or constructed program violates the IR contract."""


@dataclass(frozen=True)
class InputSpec:
    name: str
    value_type: ValueType

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("input names must be nonempty and trimmed")

    def to_record(self) -> dict[str, str]:
        return {"name": self.name, "type": self.value_type.value}


@dataclass(frozen=True)
class StaticLimits:
    maximum_nodes: int = 512
    maximum_depth: int = 64
    maximum_bindings: int = 64
    maximum_holes: int = 64
    maximum_fixed_point_steps: int = 900

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if isinstance(value, bool) or int(value) <= 0:
                raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class ProgramMetrics:
    node_count: int
    maximum_depth: int
    binding_count: int
    hole_count: int
    operator_count: int
    operator_histogram: tuple[tuple[str, int], ...]

    def to_record(self) -> dict[str, object]:
        return {
            "node_count": self.node_count,
            "maximum_depth": self.maximum_depth,
            "binding_count": self.binding_count,
            "hole_count": self.hole_count,
            "operator_count": self.operator_count,
            "operator_histogram": dict(self.operator_histogram),
        }


def children(node: Expression) -> tuple[Expression, ...]:
    if isinstance(node, (InputNode, LiteralNode, VariableNode, HoleNode)):
        return ()
    if isinstance(node, LetNode):
        return (node.value, node.body)
    if isinstance(node, CallNode):
        return node.arguments
    if isinstance(node, IfNode):
        return (node.predicate, node.when_true, node.when_false)
    if isinstance(node, CaseNode):
        return tuple(item for branch in node.branches for item in (branch.predicate, branch.result)) + (node.default,)
    if isinstance(node, MapNode):
        return (node.collection, node.body)
    if isinstance(node, FilterNode):
        return (node.collection, node.predicate)
    if isinstance(node, (SelectNode, AnyNode, AllNode)):
        return (node.collection, node.predicate)
    if isinstance(node, CountNode):
        return (node.collection,) + (() if node.predicate is None else (node.predicate,))
    if isinstance(node, FoldNode):
        return (node.collection, node.initial, node.body)
    if isinstance(node, CartesianMapNode):
        return (node.left, node.right, node.body)
    if isinstance(node, ArgExtremeNode):
        return (node.collection, node.key)
    if isinstance(node, SortNode):
        return (node.collection, node.key)
    if isinstance(node, RepeatUntilStableNode):
        return (node.seed, node.body)
    if isinstance(node, RenderNode):
        return (node.canvas, node.items) + (() if node.color is None else (node.color,))
    if isinstance(node, PackNode):
        return (node.items, node.background)
    if isinstance(node, TileNode):
        return (node.tile, node.rows, node.columns)
    raise TypeError(f"unsupported expression node {type(node)!r}")


def iter_nodes(root: Expression) -> Iterable[Expression]:
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(children(node)))


def _metrics(root: Expression) -> ProgramMetrics:
    histogram: dict[str, int] = {}
    count = bindings = holes = max_depth = 0
    stack: list[tuple[Expression, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        max_depth = max(max_depth, depth)
        if isinstance(node, (LetNode, MapNode, FilterNode, SelectNode, AnyNode, AllNode, CountNode, FoldNode, CartesianMapNode, ArgExtremeNode, SortNode, RepeatUntilStableNode)):
            bindings += 1
        if isinstance(node, HoleNode):
            holes += 1
        if isinstance(node, CallNode):
            histogram[node.operator] = histogram.get(node.operator, 0) + 1
        for child in children(node):
            stack.append((child, depth + 1))
    return ProgramMetrics(
        node_count=count,
        maximum_depth=max_depth,
        binding_count=bindings,
        hole_count=holes,
        operator_count=sum(histogram.values()),
        operator_histogram=tuple(sorted(histogram.items())),
    )


def _canonical_literal(value: object) -> None:
    json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _validate_literal(node: LiteralNode) -> None:
    _canonical_literal(node.value)
    if node.value_type == ValueType.BOOL and not isinstance(node.value, bool):
        raise ProgramValidationError("bool literals require a Boolean value")
    if node.value_type in {ValueType.INTEGER, ValueType.COLOR}:
        if isinstance(node.value, bool) or not isinstance(node.value, int):
            raise ProgramValidationError(f"{node.value_type.value} literals require an integer")
    if node.value_type == ValueType.COLOR and not 0 <= int(node.value) <= 9:
        raise ProgramValidationError("color literals must lie in [0, 9]")
    if node.value_type == ValueType.SCALAR:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ProgramValidationError("scalar literals require an integer or float")
    if node.value_type in {ValueType.DIRECTION, ValueType.SYMBOL, ValueType.COLOR_ROLE}:
        if not isinstance(node.value, str) or not node.value:
            raise ProgramValidationError(f"{node.value_type.value} literals require a nonempty string")


def validate_expression(
    node: Expression,
    registry: OperatorRegistry,
    *,
    inputs: Mapping[str, ValueType],
    scope: Mapping[str, ValueType] | None = None,
    allow_holes: bool = False,
) -> None:
    current = dict(scope or {})
    if isinstance(node, InputNode):
        if node.name not in inputs:
            raise ProgramValidationError(f"undeclared input {node.name!r}")
        if inputs[node.name] != node.value_type:
            raise ProgramValidationError(f"input {node.name!r} has an inconsistent type")
        return
    if isinstance(node, LiteralNode):
        _validate_literal(node)
        return
    if isinstance(node, VariableNode):
        if node.name not in current:
            raise ProgramValidationError(f"unbound variable {node.name!r}")
        if current[node.name] != node.value_type:
            raise ProgramValidationError(f"variable {node.name!r} has an inconsistent type")
        return
    if isinstance(node, HoleNode):
        if not allow_holes:
            raise ProgramValidationError(f"unfilled program hole {node.name!r}")
        return
    if isinstance(node, LetNode):
        validate_expression(node.value, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        nested = dict(current)
        nested[node.name] = node.value.output_type
        validate_expression(node.body, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        return
    if isinstance(node, CallNode):
        try:
            definition = registry.resolve(node.operator)
        except KeyError as error:
            raise ProgramValidationError(str(error)) from error
        if len(node.arguments) != len(definition.input_types):
            raise ProgramValidationError(
                f"operator {node.operator!r} expects {len(definition.input_types)} arguments, got {len(node.arguments)}"
            )
        for index, (argument, expected) in enumerate(zip(node.arguments, definition.input_types)):
            validate_expression(argument, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
            if argument.output_type != expected:
                raise ProgramValidationError(
                    f"operator {node.operator!r} argument {index} expects {expected.value}, got {argument.output_type.value}"
                )
        if node.value_type != definition.output_type:
            raise ProgramValidationError(
                f"operator {node.operator!r} returns {definition.output_type.value}, not {node.value_type.value}"
            )
        return
    if isinstance(node, IfNode):
        validate_expression(node.predicate, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if node.predicate.output_type != ValueType.BOOL:
            raise ProgramValidationError("if predicate must be Boolean")
        validate_expression(node.when_true, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.when_false, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        return
    if isinstance(node, CaseNode):
        for branch in node.branches:
            validate_expression(branch.predicate, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
            if branch.predicate.output_type != ValueType.BOOL:
                raise ProgramValidationError("case predicates must be Boolean")
            validate_expression(branch.result, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.default, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        return
    if isinstance(node, (MapNode, FilterNode, ArgExtremeNode, SortNode)):
        validate_expression(node.collection, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if not is_collection(node.collection.output_type):
            raise ProgramValidationError("collection combinator received a noncollection value")
        nested = dict(current)
        nested[node.variable] = element_type(node.collection.output_type)
        target = node.body if isinstance(node, MapNode) else node.predicate if isinstance(node, FilterNode) else node.key
        validate_expression(target, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        if isinstance(node, FilterNode) and node.predicate.output_type != ValueType.BOOL:
            raise ProgramValidationError("filter predicate must be Boolean")
        if isinstance(node, (ArgExtremeNode, SortNode)) and node.key.output_type not in {
            ValueType.INTEGER, ValueType.SCALAR, ValueType.COLOR, ValueType.SYMBOL
        }:
            raise ProgramValidationError("ordering keys must be integer, scalar, color, or symbol")
        return
    if isinstance(node, (SelectNode, AnyNode, AllNode)):
        validate_expression(node.collection, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        nested = dict(current)
        nested[node.variable] = element_type(node.collection.output_type)
        validate_expression(node.predicate, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        if node.predicate.output_type != ValueType.BOOL:
            raise ProgramValidationError(f"{type(node).__name__} predicate must be Boolean")
        return
    if isinstance(node, CountNode):
        validate_expression(node.collection, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if node.predicate is not None:
            nested = dict(current)
            assert node.variable is not None
            nested[node.variable] = element_type(node.collection.output_type)
            validate_expression(node.predicate, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
            if node.predicate.output_type != ValueType.BOOL:
                raise ProgramValidationError("count predicate must be Boolean")
        return
    if isinstance(node, FoldNode):
        validate_expression(node.collection, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.initial, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        nested = dict(current)
        nested[node.item_variable] = element_type(node.collection.output_type)
        nested[node.accumulator_variable] = node.initial.output_type
        validate_expression(node.body, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        if node.body.output_type != node.initial.output_type:
            raise ProgramValidationError("fold body changed the accumulator type")
        return
    if isinstance(node, CartesianMapNode):
        validate_expression(node.left, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.right, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        nested = dict(current)
        nested[node.left_variable] = element_type(node.left.output_type)
        nested[node.right_variable] = element_type(node.right.output_type)
        validate_expression(node.body, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        return
    if isinstance(node, RepeatUntilStableNode):
        validate_expression(node.seed, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        nested = dict(current)
        nested[node.state_variable] = node.seed.output_type
        validate_expression(node.body, registry, inputs=inputs, scope=nested, allow_holes=allow_holes)
        if node.body.output_type != node.seed.output_type:
            raise ProgramValidationError("fixed-point body changed the state type")
        return
    if isinstance(node, RenderNode):
        validate_expression(node.canvas, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.items, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if node.canvas.output_type != ValueType.CANVAS:
            raise ProgramValidationError("render canvas must have canvas type")
        if node.items.output_type not in {
            ValueType.OBJECT, ValueType.OBJECT_SET, ValueType.FACE, ValueType.FACE_SET,
            ValueType.CELL, ValueType.CELL_SET, ValueType.MASK,
        }:
            raise ProgramValidationError("render items have an unsupported type")
        if node.color is not None:
            validate_expression(node.color, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
            if node.color.output_type != ValueType.COLOR:
                raise ProgramValidationError("render color must have color type")
        return
    if isinstance(node, PackNode):
        validate_expression(node.items, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.background, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if node.items.output_type not in {ValueType.OBJECT_SET, ValueType.GRID_SET}:
            raise ProgramValidationError("pack items must be an object_set or grid_set")
        if node.background.output_type != ValueType.COLOR:
            raise ProgramValidationError("pack background must have color type")
        return
    if isinstance(node, TileNode):
        validate_expression(node.tile, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.rows, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        validate_expression(node.columns, registry, inputs=inputs, scope=current, allow_holes=allow_holes)
        if node.tile.output_type != ValueType.GRID:
            raise ProgramValidationError("tile input must be a grid")
        if node.rows.output_type != ValueType.INTEGER or node.columns.output_type != ValueType.INTEGER:
            raise ProgramValidationError("tile row and column counts must be integers")
        return
    raise ProgramValidationError(f"unsupported expression node {type(node)!r}")


def _alpha_node(
    node: Expression,
    *,
    input_map: Mapping[str, str],
    variable_map: Mapping[str, str],
    hole_map: dict[str, str],
    counter: list[int],
) -> Expression:
    if isinstance(node, InputNode):
        return InputNode(input_map[node.name], node.value_type)
    if isinstance(node, LiteralNode):
        return node
    if isinstance(node, VariableNode):
        return VariableNode(variable_map.get(node.name, node.name), node.value_type)
    if isinstance(node, HoleNode):
        if node.name not in hole_map:
            hole_map[node.name] = f"h{len(hole_map)}"
        return HoleNode(hole_map[node.name], node.value_type, tuple(sorted(node.domain)))
    if isinstance(node, LetNode):
        value = _alpha_node(node.value, input_map=input_map, variable_map=variable_map, hole_map=hole_map, counter=counter)
        name = f"v{counter[0]}"; counter[0] += 1
        nested = dict(variable_map); nested[node.name] = name
        return LetNode(name, value, _alpha_node(node.body, input_map=input_map, variable_map=nested, hole_map=hole_map, counter=counter))
    if isinstance(node, CallNode):
        return CallNode(node.operator, tuple(_alpha_node(arg, input_map=input_map, variable_map=variable_map, hole_map=hole_map, counter=counter) for arg in node.arguments), node.value_type)
    if isinstance(node, IfNode):
        return IfNode(*(_alpha_node(item, input_map=input_map, variable_map=variable_map, hole_map=hole_map, counter=counter) for item in (node.predicate,node.when_true,node.when_false)))
    if isinstance(node, CaseNode):
        branches=tuple(CaseBranch(
            _alpha_node(branch.predicate,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            _alpha_node(branch.result,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
        ) for branch in node.branches)
        default=_alpha_node(node.default,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        return CaseNode(branches,default)
    if isinstance(node, (MapNode, FilterNode, ArgExtremeNode, SortNode)):
        collection=_alpha_node(node.collection,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        name=f"v{counter[0]}"; counter[0]+=1
        nested=dict(variable_map);nested[node.variable]=name
        if isinstance(node,MapNode):
            return MapNode(collection,name,_alpha_node(node.body,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter))
        if isinstance(node,FilterNode):
            return FilterNode(collection,name,_alpha_node(node.predicate,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter))
        if isinstance(node,ArgExtremeNode):
            return ArgExtremeNode(collection,name,_alpha_node(node.key,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter),node.order,node.require_unique)
        return SortNode(collection,name,_alpha_node(node.key,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter),node.descending)
    if isinstance(node, (SelectNode, AnyNode, AllNode)):
        collection=_alpha_node(node.collection,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        name=f"v{counter[0]}";counter[0]+=1
        nested=dict(variable_map);nested[node.variable]=name
        predicate=_alpha_node(node.predicate,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter)
        if isinstance(node,SelectNode):return SelectNode(collection,name,predicate,node.require_unique)
        if isinstance(node,AnyNode):return AnyNode(collection,name,predicate)
        return AllNode(collection,name,predicate)
    if isinstance(node, CountNode):
        collection=_alpha_node(node.collection,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        if node.predicate is None:return CountNode(collection)
        assert node.variable is not None
        name=f"v{counter[0]}";counter[0]+=1
        nested=dict(variable_map);nested[node.variable]=name
        predicate=_alpha_node(node.predicate,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter)
        return CountNode(collection,name,predicate)
    if isinstance(node, FoldNode):
        collection=_alpha_node(node.collection,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        initial=_alpha_node(node.initial,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        item_name=f"v{counter[0]}";counter[0]+=1
        acc_name=f"v{counter[0]}";counter[0]+=1
        nested=dict(variable_map);nested[node.item_variable]=item_name;nested[node.accumulator_variable]=acc_name
        body=_alpha_node(node.body,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter)
        return FoldNode(collection,item_name,acc_name,initial,body)
    if isinstance(node, CartesianMapNode):
        left=_alpha_node(node.left,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        right=_alpha_node(node.right,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        left_name=f"v{counter[0]}";counter[0]+=1
        right_name=f"v{counter[0]}";counter[0]+=1
        nested=dict(variable_map);nested[node.left_variable]=left_name;nested[node.right_variable]=right_name
        body=_alpha_node(node.body,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter)
        return CartesianMapNode(left,right,left_name,right_name,body)
    if isinstance(node, RepeatUntilStableNode):
        seed=_alpha_node(node.seed,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter)
        name=f"v{counter[0]}";counter[0]+=1
        nested=dict(variable_map);nested[node.state_variable]=name
        body=_alpha_node(node.body,input_map=input_map,variable_map=nested,hole_map=hole_map,counter=counter)
        return RepeatUntilStableNode(seed,name,body,node.maximum_steps,node.monotone)
    if isinstance(node, RenderNode):
        return RenderNode(
            _alpha_node(node.canvas,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            _alpha_node(node.items,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            None if node.color is None else _alpha_node(node.color,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            node.mode,
        )
    if isinstance(node, PackNode):
        return PackNode(
            _alpha_node(node.items,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            _alpha_node(node.background,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter),
            node.axis,node.gap,node.normalize,
        )
    if isinstance(node, TileNode):
        return TileNode(*(_alpha_node(item,input_map=input_map,variable_map=variable_map,hole_map=hole_map,counter=counter) for item in (node.tile,node.rows,node.columns)))
    raise TypeError(type(node))


def replace_holes(node: Expression, replacements: Mapping[str, Expression]) -> Expression:
    if isinstance(node,HoleNode):
        if node.name not in replacements:
            return node
        replacement=replacements[node.name]
        if replacement.output_type!=node.value_type:
            raise TypeError(f"replacement for hole {node.name!r} has type {replacement.output_type.value}, expected {node.value_type.value}")
        return replacement
    if isinstance(node,(InputNode,LiteralNode,VariableNode)):
        return node
    if isinstance(node,LetNode):return LetNode(node.name,replace_holes(node.value,replacements),replace_holes(node.body,replacements))
    if isinstance(node,CallNode):return CallNode(node.operator,tuple(replace_holes(a,replacements) for a in node.arguments),node.value_type)
    if isinstance(node,IfNode):return IfNode(replace_holes(node.predicate,replacements),replace_holes(node.when_true,replacements),replace_holes(node.when_false,replacements))
    if isinstance(node,CaseNode):return CaseNode(tuple(CaseBranch(replace_holes(b.predicate,replacements),replace_holes(b.result,replacements)) for b in node.branches),replace_holes(node.default,replacements))
    if isinstance(node,MapNode):return MapNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.body,replacements))
    if isinstance(node,FilterNode):return FilterNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.predicate,replacements))
    if isinstance(node,SelectNode):return SelectNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.predicate,replacements),node.require_unique)
    if isinstance(node,AnyNode):return AnyNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.predicate,replacements))
    if isinstance(node,AllNode):return AllNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.predicate,replacements))
    if isinstance(node,CountNode):return CountNode(replace_holes(node.collection,replacements),node.variable,None if node.predicate is None else replace_holes(node.predicate,replacements))
    if isinstance(node,FoldNode):return FoldNode(replace_holes(node.collection,replacements),node.item_variable,node.accumulator_variable,replace_holes(node.initial,replacements),replace_holes(node.body,replacements))
    if isinstance(node,CartesianMapNode):return CartesianMapNode(replace_holes(node.left,replacements),replace_holes(node.right,replacements),node.left_variable,node.right_variable,replace_holes(node.body,replacements))
    if isinstance(node,ArgExtremeNode):return ArgExtremeNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.key,replacements),node.order,node.require_unique)
    if isinstance(node,SortNode):return SortNode(replace_holes(node.collection,replacements),node.variable,replace_holes(node.key,replacements),node.descending)
    if isinstance(node,RepeatUntilStableNode):return RepeatUntilStableNode(replace_holes(node.seed,replacements),node.state_variable,replace_holes(node.body,replacements),node.maximum_steps,node.monotone)
    if isinstance(node,RenderNode):return RenderNode(replace_holes(node.canvas,replacements),replace_holes(node.items,replacements),None if node.color is None else replace_holes(node.color,replacements),node.mode)
    if isinstance(node,PackNode):return PackNode(replace_holes(node.items,replacements),replace_holes(node.background,replacements),node.axis,node.gap,node.normalize)
    if isinstance(node,TileNode):return TileNode(replace_holes(node.tile,replacements),replace_holes(node.rows,replacements),replace_holes(node.columns,replacements))
    raise TypeError(type(node))


@dataclass(frozen=True)
class Program:
    inputs: tuple[InputSpec, ...]
    root: Expression
    schema_version: int = IR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != IR_SCHEMA_VERSION:
            raise ValueError(f"unsupported Program IR version {self.schema_version}")
        names=[item.name for item in self.inputs]
        if len(set(names))!=len(names):
            raise ValueError("program inputs must have unique names")

    @property
    def output_type(self) -> ValueType:
        return self.root.output_type

    @property
    def metrics(self) -> ProgramMetrics:
        return _metrics(self.root)

    @property
    def executable(self) -> bool:
        return self.metrics.hole_count == 0

    def validate(self, registry: OperatorRegistry, *, allow_holes: bool=False, limits: StaticLimits=StaticLimits()) -> ProgramMetrics:
        metrics=self.metrics
        if metrics.node_count>limits.maximum_nodes:raise ProgramValidationError("program node budget exceeded")
        if metrics.maximum_depth>limits.maximum_depth:raise ProgramValidationError("program depth budget exceeded")
        if metrics.binding_count>limits.maximum_bindings:raise ProgramValidationError("program binding budget exceeded")
        if metrics.hole_count>limits.maximum_holes:raise ProgramValidationError("program hole budget exceeded")
        for node in iter_nodes(self.root):
            if isinstance(node,RepeatUntilStableNode) and node.maximum_steps>limits.maximum_fixed_point_steps:
                raise ProgramValidationError("fixed-point step budget exceeded")
        validate_expression(self.root,registry,inputs={item.name:item.value_type for item in self.inputs},allow_holes=allow_holes)
        return metrics

    def alpha_normalized(self) -> "Program":
        input_map={item.name:f"input{index}" for index,item in enumerate(self.inputs)}
        inputs=tuple(InputSpec(input_map[item.name],item.value_type) for item in self.inputs)
        root=_alpha_node(self.root,input_map=input_map,variable_map={},hole_map={},counter=[0])
        return Program(inputs,root,self.schema_version)

    def to_record(self, *, canonical: bool=True) -> dict[str,object]:
        target=self.alpha_normalized() if canonical else self
        return {
            "schema":IR_SCHEMA,
            "schema_version":target.schema_version,
            "inputs":[item.to_record() for item in target.inputs],
            "output_type":target.output_type.value,
            "root":node_to_record(target.root),
        }

    def to_json(self, *, canonical: bool=True) -> str:
        return json.dumps(self.to_record(canonical=canonical),sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

    def content_hash(self) -> str:
        return hashlib.sha256(self.to_json(canonical=True).encode("utf-8")).hexdigest()

    def fill(self,replacements:Mapping[str,Expression]) -> "Program":
        return Program(self.inputs,replace_holes(self.root,replacements),self.schema_version)

    @classmethod
    def from_record(cls,raw:object) -> "Program":
        if not isinstance(raw,Mapping):raise TypeError("program record must be a mapping")
        if raw.get("schema")!=IR_SCHEMA:raise ValueError(f"unknown Program IR schema {raw.get('schema')!r}")
        raw_inputs=raw.get("inputs")
        if not isinstance(raw_inputs,list):raise TypeError("program inputs must be a list")
        inputs=[]
        for item in raw_inputs:
            if not isinstance(item,Mapping):raise TypeError("input records must be mappings")
            inputs.append(InputSpec(str(item["name"]),ValueType(str(item["type"]))))
        program=cls(tuple(inputs),node_from_record(raw.get("root")),int(raw.get("schema_version",-1)))
        if ValueType(str(raw.get("output_type")))!=program.output_type:raise ProgramValidationError("declared output type does not match the root")
        return program

    @classmethod
    def from_json(cls,payload:str)->"Program":
        return cls.from_record(json.loads(payload))


__all__=[
    "IR_SCHEMA","IR_SCHEMA_VERSION","InputSpec","Program","ProgramMetrics",
    "ProgramValidationError","StaticLimits","children","iter_nodes",
    "replace_holes","validate_expression",
]
