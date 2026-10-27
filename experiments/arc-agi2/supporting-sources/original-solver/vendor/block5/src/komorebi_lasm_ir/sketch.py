"""Typed anti-unification and hole filling for Program IR v2."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Sequence

from .nodes import (
    AllNode, AnyNode, ArgExtremeNode, CallNode, CartesianMapNode, CaseBranch,
    CaseNode, CountNode, Expression, FilterNode, FoldNode, HoleNode, IfNode,
    InputNode, LetNode, LiteralNode, MapNode, PackNode, RenderNode,
    RepeatUntilStableNode, SelectNode, SortNode, TileNode, VariableNode,
    node_to_record,
)
from .program import Program, iter_nodes


def _node_hash(node: Expression) -> str:
    payload = json.dumps(node_to_record(node), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProgramSketch:
    program: Program
    source_program_hashes: tuple[str, ...]

    @property
    def holes(self) -> tuple[HoleNode, ...]:
        by_name = {
            node.name: node
            for node in iter_nodes(self.program.root)
            if isinstance(node, HoleNode)
        }
        return tuple(by_name[name] for name in sorted(by_name))

    @property
    def hole_count(self) -> int:
        return len(self.holes)

    def to_record(self) -> dict[str, object]:
        return {
            "schema": "komorebi.lasm_program_sketch",
            "schema_version": 1,
            "program": self.program.to_record(),
            "source_program_hashes": list(self.source_program_hashes),
            "hole_count": self.hole_count,
        }


def _hole(nodes: Sequence[Expression], counter: list[int]) -> HoleNode:
    output_type = nodes[0].output_type
    if any(node.output_type != output_type for node in nodes):
        raise TypeError("cannot anti-unify expressions with different output types")
    name = f"hole{counter[0]}"
    counter[0] += 1
    return HoleNode(name, output_type, tuple(sorted({_node_hash(node) for node in nodes})))


def _anti(nodes: Sequence[Expression], counter: list[int]) -> Expression:
    first = nodes[0]
    if all(node == first for node in nodes[1:]):
        return first
    if any(node.output_type != first.output_type for node in nodes[1:]):
        raise TypeError("cannot anti-unify expressions with different output types")
    if all(type(node) is type(first) for node in nodes):
        if isinstance(first, InputNode):
            if all(node.name == first.name and node.value_type == first.value_type for node in nodes):
                return first
        elif isinstance(first, VariableNode):
            if all(node.name == first.name and node.value_type == first.value_type for node in nodes):
                return first
        elif isinstance(first, LiteralNode):
            return _hole(nodes, counter)
        elif isinstance(first, HoleNode):
            return _hole(nodes, counter)
        elif isinstance(first, CallNode):
            if all(
                node.operator == first.operator
                and node.value_type == first.value_type
                and len(node.arguments) == len(first.arguments)
                for node in nodes
            ):
                return CallNode(
                    first.operator,
                    tuple(_anti(tuple(node.arguments[index] for node in nodes), counter) for index in range(len(first.arguments))),
                    first.value_type,
                )
        elif isinstance(first, LetNode):
            if all(node.name == first.name for node in nodes):
                return LetNode(
                    first.name,
                    _anti(tuple(node.value for node in nodes), counter),
                    _anti(tuple(node.body for node in nodes), counter),
                )
        elif isinstance(first, IfNode):
            return IfNode(
                _anti(tuple(node.predicate for node in nodes), counter),
                _anti(tuple(node.when_true for node in nodes), counter),
                _anti(tuple(node.when_false for node in nodes), counter),
            )
        elif isinstance(first, CaseNode):
            if all(len(node.branches) == len(first.branches) for node in nodes):
                branches = []
                for index in range(len(first.branches)):
                    branches.append(
                        CaseBranch(
                            _anti(tuple(node.branches[index].predicate for node in nodes), counter),
                            _anti(tuple(node.branches[index].result for node in nodes), counter),
                        )
                    )
                return CaseNode(tuple(branches), _anti(tuple(node.default for node in nodes), counter))
        elif isinstance(first, MapNode):
            if all(node.variable == first.variable for node in nodes):
                return MapNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.body for node in nodes), counter),
                )
        elif isinstance(first, FilterNode):
            if all(node.variable == first.variable for node in nodes):
                return FilterNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.predicate for node in nodes), counter),
                )
        elif isinstance(first, SelectNode):
            if all(node.variable == first.variable and node.require_unique == first.require_unique for node in nodes):
                return SelectNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.predicate for node in nodes), counter),
                    first.require_unique,
                )
        elif isinstance(first, AnyNode):
            if all(node.variable == first.variable for node in nodes):
                return AnyNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.predicate for node in nodes), counter),
                )
        elif isinstance(first, AllNode):
            if all(node.variable == first.variable for node in nodes):
                return AllNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.predicate for node in nodes), counter),
                )
        elif isinstance(first, CountNode):
            if all((node.variable is None) == (first.variable is None) for node in nodes):
                collection = _anti(tuple(node.collection for node in nodes), counter)
                if first.predicate is None:
                    return CountNode(collection)
                if all(node.variable == first.variable for node in nodes):
                    return CountNode(
                        collection,
                        first.variable,
                        _anti(tuple(node.predicate for node in nodes if node.predicate is not None), counter),
                    )
        elif isinstance(first, FoldNode):
            if all(
                node.item_variable == first.item_variable
                and node.accumulator_variable == first.accumulator_variable
                for node in nodes
            ):
                return FoldNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.item_variable,
                    first.accumulator_variable,
                    _anti(tuple(node.initial for node in nodes), counter),
                    _anti(tuple(node.body for node in nodes), counter),
                )
        elif isinstance(first, CartesianMapNode):
            if all(
                node.left_variable == first.left_variable
                and node.right_variable == first.right_variable
                for node in nodes
            ):
                return CartesianMapNode(
                    _anti(tuple(node.left for node in nodes), counter),
                    _anti(tuple(node.right for node in nodes), counter),
                    first.left_variable,
                    first.right_variable,
                    _anti(tuple(node.body for node in nodes), counter),
                )
        elif isinstance(first, ArgExtremeNode):
            if all(
                node.variable == first.variable
                and node.order == first.order
                and node.require_unique == first.require_unique
                for node in nodes
            ):
                return ArgExtremeNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.key for node in nodes), counter),
                    first.order,
                    first.require_unique,
                )
        elif isinstance(first, SortNode):
            if all(node.variable == first.variable and node.descending == first.descending for node in nodes):
                return SortNode(
                    _anti(tuple(node.collection for node in nodes), counter),
                    first.variable,
                    _anti(tuple(node.key for node in nodes), counter),
                    first.descending,
                )
        elif isinstance(first, RepeatUntilStableNode):
            if all(
                node.state_variable == first.state_variable
                and node.maximum_steps == first.maximum_steps
                and node.monotone == first.monotone
                for node in nodes
            ):
                return RepeatUntilStableNode(
                    _anti(tuple(node.seed for node in nodes), counter),
                    first.state_variable,
                    _anti(tuple(node.body for node in nodes), counter),
                    first.maximum_steps,
                    first.monotone,
                )
        elif isinstance(first, RenderNode):
            if all(node.mode == first.mode and (node.color is None) == (first.color is None) for node in nodes):
                colors = None if first.color is None else _anti(tuple(node.color for node in nodes if node.color is not None), counter)
                return RenderNode(
                    _anti(tuple(node.canvas for node in nodes), counter),
                    _anti(tuple(node.items for node in nodes), counter),
                    colors,
                    first.mode,
                )
        elif isinstance(first, PackNode):
            if all(node.axis == first.axis and node.gap == first.gap and node.normalize == first.normalize for node in nodes):
                return PackNode(
                    _anti(tuple(node.items for node in nodes), counter),
                    _anti(tuple(node.background for node in nodes), counter),
                    first.axis,
                    first.gap,
                    first.normalize,
                )
        elif isinstance(first, TileNode):
            return TileNode(
                _anti(tuple(node.tile for node in nodes), counter),
                _anti(tuple(node.rows for node in nodes), counter),
                _anti(tuple(node.columns for node in nodes), counter),
            )
    return _hole(nodes, counter)


def anti_unify_programs(programs: Sequence[Program]) -> ProgramSketch:
    if len(programs) < 2:
        raise ValueError("anti-unification requires at least two programs")
    normalized = tuple(program.alpha_normalized() for program in programs)
    first = normalized[0]
    if any(program.inputs != first.inputs for program in normalized[1:]):
        raise TypeError("program input signatures differ")
    if any(program.output_type != first.output_type for program in normalized[1:]):
        raise TypeError("program output types differ")
    root = _anti(tuple(program.root for program in normalized), [0])
    return ProgramSketch(
        program=Program(first.inputs, root),
        source_program_hashes=tuple(sorted(program.content_hash() for program in programs)),
    )


__all__ = ["ProgramSketch", "anti_unify_programs"]
