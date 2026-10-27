"""Canonical expression nodes for LASM Program IR v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence, TypeAlias

from .types import ValueType, collection_type, element_type, is_collection


def _valid_name(name: str, context: str) -> None:
    if not isinstance(name, str) or not name or name.strip() != name:
        raise ValueError(f"{context} names must be nonempty and trimmed")


@dataclass(frozen=True)
class InputNode:
    name: str
    value_type: ValueType

    def __post_init__(self) -> None:
        _valid_name(self.name, "input")

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class LiteralNode:
    value_type: ValueType
    value: object

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class VariableNode:
    name: str
    value_type: ValueType

    def __post_init__(self) -> None:
        _valid_name(self.name, "variable")

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class HoleNode:
    """Typed, non-executable slot used by inverse compilation and anti-unification."""

    name: str
    value_type: ValueType
    domain: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _valid_name(self.name, "hole")
        if len(set(self.domain)) != len(self.domain):
            raise ValueError("hole domains cannot contain duplicate alternatives")

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class LetNode:
    name: str
    value: "Expression"
    body: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.name, "binding")

    @property
    def output_type(self) -> ValueType:
        return self.body.output_type


@dataclass(frozen=True)
class CallNode:
    operator: str
    arguments: tuple["Expression", ...]
    value_type: ValueType

    def __post_init__(self) -> None:
        _valid_name(self.operator, "operator")

    @property
    def output_type(self) -> ValueType:
        return self.value_type


@dataclass(frozen=True)
class IfNode:
    predicate: "Expression"
    when_true: "Expression"
    when_false: "Expression"

    def __post_init__(self) -> None:
        if self.when_true.output_type != self.when_false.output_type:
            raise TypeError("if branches must have the same output type")

    @property
    def output_type(self) -> ValueType:
        return self.when_true.output_type


@dataclass(frozen=True)
class CaseBranch:
    predicate: "Expression"
    result: "Expression"


@dataclass(frozen=True)
class CaseNode:
    branches: tuple[CaseBranch, ...]
    default: "Expression"

    def __post_init__(self) -> None:
        if not self.branches:
            raise ValueError("a case expression requires at least one branch")
        if any(branch.result.output_type != self.default.output_type for branch in self.branches):
            raise TypeError("all case branches must have the default output type")

    @property
    def output_type(self) -> ValueType:
        return self.default.output_type


@dataclass(frozen=True)
class MapNode:
    collection: "Expression"
    variable: str
    body: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.variable, "map variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("map input must have a collection type")
        collection_type(self.body.output_type)

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return collection_type(self.body.output_type)


@dataclass(frozen=True)
class FilterNode:
    collection: "Expression"
    variable: str
    predicate: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.variable, "filter variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("filter input must have a collection type")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return self.collection.output_type




@dataclass(frozen=True)
class SelectNode:
    """Select a predicate-matching collection element, failing on absence or ambiguity."""

    collection: "Expression"
    variable: str
    predicate: "Expression"
    require_unique: bool = True

    def __post_init__(self) -> None:
        _valid_name(self.variable, "select variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("select input must have a collection type")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return self.variable_type


@dataclass(frozen=True)
class AnyNode:
    collection: "Expression"
    variable: str
    predicate: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.variable, "any variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("any input must have a collection type")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return ValueType.BOOL


@dataclass(frozen=True)
class AllNode:
    collection: "Expression"
    variable: str
    predicate: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.variable, "all variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("all input must have a collection type")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return ValueType.BOOL


@dataclass(frozen=True)
class CountNode:
    collection: "Expression"
    variable: str | None = None
    predicate: "Expression | None" = None

    def __post_init__(self) -> None:
        if not is_collection(self.collection.output_type):
            raise TypeError("count input must have a collection type")
        if (self.variable is None) != (self.predicate is None):
            raise ValueError("count variable and predicate must be supplied together")
        if self.variable is not None:
            _valid_name(self.variable, "count variable")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return ValueType.INTEGER


@dataclass(frozen=True)
class FoldNode:
    """Left fold over a finite collection with typed item and accumulator binders."""

    collection: "Expression"
    item_variable: str
    accumulator_variable: str
    initial: "Expression"
    body: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.item_variable, "fold item variable")
        _valid_name(self.accumulator_variable, "fold accumulator variable")
        if self.item_variable == self.accumulator_variable:
            raise ValueError("fold item and accumulator variables must be distinct")
        if not is_collection(self.collection.output_type):
            raise TypeError("fold input must have a collection type")
        if self.initial.output_type != self.body.output_type:
            raise TypeError("fold body must preserve the accumulator type")

    @property
    def item_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return self.initial.output_type


@dataclass(frozen=True)
class CartesianMapNode:
    """Map a typed body over the Cartesian product of two finite collections."""

    left: "Expression"
    right: "Expression"
    left_variable: str
    right_variable: str
    body: "Expression"

    def __post_init__(self) -> None:
        _valid_name(self.left_variable, "Cartesian left variable")
        _valid_name(self.right_variable, "Cartesian right variable")
        if self.left_variable == self.right_variable:
            raise ValueError("Cartesian variables must be distinct")
        if not is_collection(self.left.output_type) or not is_collection(self.right.output_type):
            raise TypeError("Cartesian map inputs must have collection types")
        collection_type(self.body.output_type)

    @property
    def left_type(self) -> ValueType:
        return element_type(self.left.output_type)

    @property
    def right_type(self) -> ValueType:
        return element_type(self.right.output_type)

    @property
    def output_type(self) -> ValueType:
        return collection_type(self.body.output_type)


@dataclass(frozen=True)
class ArgExtremeNode:
    collection: "Expression"
    variable: str
    key: "Expression"
    order: str = "maximum"
    require_unique: bool = True

    def __post_init__(self) -> None:
        _valid_name(self.variable, "arg-extreme variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("arg-extreme input must have a collection type")
        if self.order not in {"minimum", "maximum"}:
            raise ValueError("arg-extreme order must be minimum or maximum")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return self.variable_type


@dataclass(frozen=True)
class SortNode:
    collection: "Expression"
    variable: str
    key: "Expression"
    descending: bool = False

    def __post_init__(self) -> None:
        _valid_name(self.variable, "sort variable")
        if not is_collection(self.collection.output_type):
            raise TypeError("sort input must have a collection type")

    @property
    def variable_type(self) -> ValueType:
        return element_type(self.collection.output_type)

    @property
    def output_type(self) -> ValueType:
        return self.collection.output_type


@dataclass(frozen=True)
class RepeatUntilStableNode:
    seed: "Expression"
    state_variable: str
    body: "Expression"
    maximum_steps: int
    monotone: bool = False

    def __post_init__(self) -> None:
        _valid_name(self.state_variable, "fixed-point variable")
        if isinstance(self.maximum_steps, bool) or int(self.maximum_steps) <= 0:
            raise ValueError("maximum_steps must be a positive integer")
        if self.seed.output_type != self.body.output_type:
            raise TypeError("fixed-point seed and body must have the same type")

    @property
    def output_type(self) -> ValueType:
        return self.seed.output_type


@dataclass(frozen=True)
class RenderNode:
    """Render objects, faces, cells, or a mask onto an immutable canvas."""

    canvas: "Expression"
    items: "Expression"
    color: "Expression | None" = None
    mode: str = "paint"

    def __post_init__(self) -> None:
        if self.mode not in {"paint", "erase", "preserve"}:
            raise ValueError("render mode must be paint, erase, or preserve")

    @property
    def output_type(self) -> ValueType:
        return ValueType.GRID


@dataclass(frozen=True)
class PackNode:
    """Normalize and pack an object or grid collection into a constructed canvas."""

    items: "Expression"
    background: "Expression"
    axis: str = "row"
    gap: int = 0
    normalize: bool = True

    def __post_init__(self) -> None:
        if self.axis not in {"row", "column", "grid"}:
            raise ValueError("pack axis must be row, column, or grid")
        if isinstance(self.gap, bool) or int(self.gap) < 0:
            raise ValueError("pack gap must be a nonnegative integer")

    @property
    def output_type(self) -> ValueType:
        return ValueType.GRID


@dataclass(frozen=True)
class TileNode:
    tile: "Expression"
    rows: "Expression"
    columns: "Expression"

    @property
    def output_type(self) -> ValueType:
        return ValueType.GRID


Expression: TypeAlias = (
    InputNode
    | LiteralNode
    | VariableNode
    | HoleNode
    | LetNode
    | CallNode
    | IfNode
    | CaseNode
    | MapNode
    | FilterNode
    | SelectNode
    | AnyNode
    | AllNode
    | CountNode
    | FoldNode
    | CartesianMapNode
    | ArgExtremeNode
    | SortNode
    | RepeatUntilStableNode
    | RenderNode
    | PackNode
    | TileNode
)


def _literal_value(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, tuple):
        return [_literal_value(item) for item in value]
    if isinstance(value, list):
        return [_literal_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _literal_value(item) for key, item in value.items()}
    raise TypeError(f"literal value is not canonically serializable: {type(value)!r}")


def node_to_record(node: Expression) -> dict[str, object]:
    if isinstance(node, InputNode):
        return {"kind": "input", "name": node.name, "type": node.value_type.value}
    if isinstance(node, LiteralNode):
        return {"kind": "literal", "type": node.value_type.value, "value": _literal_value(node.value)}
    if isinstance(node, VariableNode):
        return {"kind": "variable", "name": node.name, "type": node.value_type.value}
    if isinstance(node, HoleNode):
        return {"kind": "hole", "name": node.name, "type": node.value_type.value, "domain": list(node.domain)}
    if isinstance(node, LetNode):
        return {"kind": "let", "name": node.name, "value": node_to_record(node.value), "body": node_to_record(node.body)}
    if isinstance(node, CallNode):
        return {"kind": "call", "operator": node.operator, "type": node.value_type.value, "arguments": [node_to_record(arg) for arg in node.arguments]}
    if isinstance(node, IfNode):
        return {"kind": "if", "predicate": node_to_record(node.predicate), "true": node_to_record(node.when_true), "false": node_to_record(node.when_false)}
    if isinstance(node, CaseNode):
        return {"kind": "case", "branches": [{"predicate": node_to_record(b.predicate), "result": node_to_record(b.result)} for b in node.branches], "default": node_to_record(node.default)}
    if isinstance(node, MapNode):
        return {"kind": "map", "collection": node_to_record(node.collection), "variable": node.variable, "body": node_to_record(node.body)}
    if isinstance(node, FilterNode):
        return {"kind": "filter", "collection": node_to_record(node.collection), "variable": node.variable, "predicate": node_to_record(node.predicate)}
    if isinstance(node, SelectNode):
        return {"kind": "select", "collection": node_to_record(node.collection), "variable": node.variable, "predicate": node_to_record(node.predicate), "require_unique": node.require_unique}
    if isinstance(node, AnyNode):
        return {"kind": "any", "collection": node_to_record(node.collection), "variable": node.variable, "predicate": node_to_record(node.predicate)}
    if isinstance(node, AllNode):
        return {"kind": "all", "collection": node_to_record(node.collection), "variable": node.variable, "predicate": node_to_record(node.predicate)}
    if isinstance(node, CountNode):
        return {"kind": "count", "collection": node_to_record(node.collection), "variable": node.variable, "predicate": None if node.predicate is None else node_to_record(node.predicate)}
    if isinstance(node, FoldNode):
        return {"kind": "fold", "collection": node_to_record(node.collection), "item_variable": node.item_variable, "accumulator_variable": node.accumulator_variable, "initial": node_to_record(node.initial), "body": node_to_record(node.body)}
    if isinstance(node, CartesianMapNode):
        return {"kind": "cartesian_map", "left": node_to_record(node.left), "right": node_to_record(node.right), "left_variable": node.left_variable, "right_variable": node.right_variable, "body": node_to_record(node.body)}
    if isinstance(node, ArgExtremeNode):
        return {"kind": "arg_extreme", "collection": node_to_record(node.collection), "variable": node.variable, "key": node_to_record(node.key), "order": node.order, "require_unique": node.require_unique}
    if isinstance(node, SortNode):
        return {"kind": "sort", "collection": node_to_record(node.collection), "variable": node.variable, "key": node_to_record(node.key), "descending": node.descending}
    if isinstance(node, RepeatUntilStableNode):
        return {"kind": "repeat_until_stable", "seed": node_to_record(node.seed), "state_variable": node.state_variable, "body": node_to_record(node.body), "maximum_steps": int(node.maximum_steps), "monotone": bool(node.monotone)}
    if isinstance(node, RenderNode):
        return {"kind": "render", "canvas": node_to_record(node.canvas), "items": node_to_record(node.items), "color": None if node.color is None else node_to_record(node.color), "mode": node.mode}
    if isinstance(node, PackNode):
        return {"kind": "pack", "items": node_to_record(node.items), "background": node_to_record(node.background), "axis": node.axis, "gap": int(node.gap), "normalize": bool(node.normalize)}
    if isinstance(node, TileNode):
        return {"kind": "tile", "tile": node_to_record(node.tile), "rows": node_to_record(node.rows), "columns": node_to_record(node.columns)}
    raise TypeError(f"unsupported expression node {type(node)!r}")


def _mapping(raw: object, context: str) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        raise TypeError(f"{context} must be a mapping")
    return raw


def node_from_record(raw: object) -> Expression:
    record = _mapping(raw, "expression")
    kind = record.get("kind")
    if kind == "input":
        return InputNode(str(record["name"]), ValueType(str(record["type"])))
    if kind == "literal":
        return LiteralNode(ValueType(str(record["type"])), record.get("value"))
    if kind == "variable":
        return VariableNode(str(record["name"]), ValueType(str(record["type"])))
    if kind == "hole":
        domain = record.get("domain", [])
        if not isinstance(domain, list):
            raise TypeError("hole domain must be a list")
        return HoleNode(str(record["name"]), ValueType(str(record["type"])), tuple(str(item) for item in domain))
    if kind == "let":
        return LetNode(str(record["name"]), node_from_record(record["value"]), node_from_record(record["body"]))
    if kind == "call":
        args = record.get("arguments")
        if not isinstance(args, list):
            raise TypeError("call arguments must be a list")
        return CallNode(str(record["operator"]), tuple(node_from_record(arg) for arg in args), ValueType(str(record["type"])))
    if kind == "if":
        return IfNode(node_from_record(record["predicate"]), node_from_record(record["true"]), node_from_record(record["false"]))
    if kind == "case":
        raw_branches = record.get("branches")
        if not isinstance(raw_branches, list):
            raise TypeError("case branches must be a list")
        branches = []
        for raw_branch in raw_branches:
            branch = _mapping(raw_branch, "case branch")
            branches.append(CaseBranch(node_from_record(branch["predicate"]), node_from_record(branch["result"])))
        return CaseNode(tuple(branches), node_from_record(record["default"]))
    if kind == "map":
        return MapNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["body"]))
    if kind == "filter":
        return FilterNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["predicate"]))
    if kind == "select":
        return SelectNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["predicate"]), bool(record.get("require_unique", True)))
    if kind == "any":
        return AnyNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["predicate"]))
    if kind == "all":
        return AllNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["predicate"]))
    if kind == "count":
        predicate = record.get("predicate")
        variable = record.get("variable")
        return CountNode(node_from_record(record["collection"]), None if variable is None else str(variable), None if predicate is None else node_from_record(predicate))
    if kind == "fold":
        return FoldNode(node_from_record(record["collection"]), str(record["item_variable"]), str(record["accumulator_variable"]), node_from_record(record["initial"]), node_from_record(record["body"]))
    if kind == "cartesian_map":
        return CartesianMapNode(node_from_record(record["left"]), node_from_record(record["right"]), str(record["left_variable"]), str(record["right_variable"]), node_from_record(record["body"]))
    if kind == "arg_extreme":
        return ArgExtremeNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["key"]), str(record.get("order", "maximum")), bool(record.get("require_unique", True)))
    if kind == "sort":
        return SortNode(node_from_record(record["collection"]), str(record["variable"]), node_from_record(record["key"]), bool(record.get("descending", False)))
    if kind == "repeat_until_stable":
        return RepeatUntilStableNode(node_from_record(record["seed"]), str(record["state_variable"]), node_from_record(record["body"]), int(record["maximum_steps"]), bool(record.get("monotone", False)))
    if kind == "render":
        raw_color = record.get("color")
        return RenderNode(node_from_record(record["canvas"]), node_from_record(record["items"]), None if raw_color is None else node_from_record(raw_color), str(record.get("mode", "paint")))
    if kind == "pack":
        return PackNode(node_from_record(record["items"]), node_from_record(record["background"]), str(record.get("axis", "row")), int(record.get("gap", 0)), bool(record.get("normalize", True)))
    if kind == "tile":
        return TileNode(node_from_record(record["tile"]), node_from_record(record["rows"]), node_from_record(record["columns"]))
    raise ValueError(f"unknown expression kind {kind!r}")


__all__ = [
    "AllNode", "AnyNode", "ArgExtremeNode", "CallNode", "CartesianMapNode",
    "CaseBranch", "CaseNode", "CountNode", "Expression", "FilterNode",
    "FoldNode", "HoleNode", "IfNode", "InputNode", "LetNode",
    "LiteralNode", "MapNode", "PackNode", "RenderNode",
    "RepeatUntilStableNode", "SelectNode", "SortNode", "TileNode",
    "VariableNode", "node_from_record", "node_to_record",
]
