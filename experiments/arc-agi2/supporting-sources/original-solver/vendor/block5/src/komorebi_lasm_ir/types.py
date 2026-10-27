"""Finite value types for the LASM relational program language."""

from __future__ import annotations

from enum import Enum


class ValueType(str, Enum):
    """Closed type vocabulary used by Program IR v2.

    Collection types are explicit rather than dynamically parameterized.  This
    keeps serialized programs finite, easy to audit, and portable across
    runtimes without a separate type-expression parser.
    """

    GRID = "grid"
    GRID_SET = "grid_set"
    MASK = "mask"
    BOOL = "bool"
    INTEGER = "integer"
    SCALAR = "scalar"
    SCALAR_SET = "scalar_set"
    COLOR = "color"
    COLOR_SET = "color_set"
    COLOR_ROLE = "color_role"
    SYMBOL = "symbol"
    CELL = "cell"
    CELL_SET = "cell_set"
    DIRECTION = "direction"
    BOX = "box"
    OBJECT = "object"
    OBJECT_SET = "object_set"
    FACE = "face"
    FACE_SET = "face_set"
    RELATION = "relation"
    RELATION_SET = "relation_set"
    EDIT = "edit"
    EDIT_SET = "edit_set"
    SCENE = "scene"
    LAYOUT = "layout"
    CANVAS = "canvas"
    PROGRAM = "program"


COLLECTION_ELEMENT: dict[ValueType, ValueType] = {
    ValueType.GRID_SET: ValueType.GRID,
    ValueType.SCALAR_SET: ValueType.SCALAR,
    ValueType.COLOR_SET: ValueType.COLOR,
    ValueType.CELL_SET: ValueType.CELL,
    ValueType.OBJECT_SET: ValueType.OBJECT,
    ValueType.FACE_SET: ValueType.FACE,
    ValueType.RELATION_SET: ValueType.RELATION,
    ValueType.EDIT_SET: ValueType.EDIT,
}

ELEMENT_COLLECTION: dict[ValueType, ValueType] = {
    element: collection for collection, element in COLLECTION_ELEMENT.items()
}


def is_collection(value_type: ValueType) -> bool:
    return value_type in COLLECTION_ELEMENT


def element_type(collection_type: ValueType) -> ValueType:
    try:
        return COLLECTION_ELEMENT[collection_type]
    except KeyError as error:
        raise TypeError(f"{collection_type.value} is not a collection type") from error


def collection_type(item_type: ValueType) -> ValueType:
    try:
        return ELEMENT_COLLECTION[item_type]
    except KeyError as error:
        raise TypeError(f"no collection type is declared for {item_type.value}") from error


__all__ = [
    "COLLECTION_ELEMENT",
    "ELEMENT_COLLECTION",
    "ValueType",
    "collection_type",
    "element_type",
    "is_collection",
]
