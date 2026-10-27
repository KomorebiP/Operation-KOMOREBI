"""Reference programs that exercise the expanded language without task IDs."""

from __future__ import annotations

from .nodes import (
    ArgExtremeNode, CallNode, FilterNode, IfNode, InputNode, LetNode,
    LiteralNode, MapNode, PackNode, RenderNode, RepeatUntilStableNode,
    SortNode, VariableNode,
)
from .program import InputSpec, Program
from .types import ValueType


def call(name: str, value_type: ValueType, *arguments: object) -> CallNode:
    return CallNode(name, tuple(arguments), value_type)


def recolor_largest_with_smallest_color_program() -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    objects_v = VariableNode("objects", ValueType.OBJECT_SET)
    ref_v = VariableNode("reference", ValueType.OBJECT)
    subject_v = VariableNode("subject", ValueType.OBJECT)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "objects",
            call("foreground_objects", ValueType.OBJECT_SET, scene_v),
            LetNode(
                "reference",
                ArgExtremeNode(
                    objects_v,
                    "candidate",
                    call("object_area", ValueType.SCALAR, VariableNode("candidate", ValueType.OBJECT)),
                    "minimum",
                    True,
                ),
                LetNode(
                    "subject",
                    ArgExtremeNode(
                        objects_v,
                        "candidate",
                        call("object_area", ValueType.SCALAR, VariableNode("candidate", ValueType.OBJECT)),
                        "maximum",
                        True,
                    ),
                    RenderNode(
                        call("canvas_from_grid", ValueType.CANVAS, grid),
                        call("object_set_singleton", ValueType.OBJECT_SET, subject_v),
                        call("object_color", ValueType.COLOR, ref_v),
                        "paint",
                    ),
                ),
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


def recolor_all_objects_to_smallest_color_program() -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    objects_v = VariableNode("objects", ValueType.OBJECT_SET)
    reference_v = VariableNode("reference", ValueType.OBJECT)
    recolored_v = VariableNode("recolored", ValueType.OBJECT_SET)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "objects",
            call("foreground_objects", ValueType.OBJECT_SET, scene_v),
            LetNode(
                "reference",
                ArgExtremeNode(
                    objects_v,
                    "candidate",
                    call("object_area", ValueType.SCALAR, VariableNode("candidate", ValueType.OBJECT)),
                    "minimum",
                ),
                LetNode(
                    "recolored",
                    MapNode(
                        objects_v,
                        "item",
                        call(
                            "recolor_object",
                            ValueType.OBJECT,
                            VariableNode("item", ValueType.OBJECT),
                            call("object_color", ValueType.COLOR, reference_v),
                        ),
                    ),
                    RenderNode(
                        call(
                            "blank_canvas_like",
                            ValueType.CANVAS,
                            grid,
                            call("background_color", ValueType.COLOR, scene_v),
                        ),
                        recolored_v,
                        None,
                        "paint",
                    ),
                ),
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


def fill_holes_with_smallest_object_color_program() -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    objects_v = VariableNode("objects", ValueType.OBJECT_SET)
    reference_v = VariableNode("reference", ValueType.OBJECT)
    holes_v = VariableNode("holes", ValueType.FACE_SET)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "objects",
            call("foreground_objects", ValueType.OBJECT_SET, scene_v),
            LetNode(
                "reference",
                ArgExtremeNode(
                    objects_v,
                    "candidate",
                    call("object_area", ValueType.SCALAR, VariableNode("candidate", ValueType.OBJECT)),
                    "minimum",
                ),
                LetNode(
                    "holes",
                    FilterNode(
                        call("ambient_faces", ValueType.FACE_SET, scene_v),
                        "face",
                        call("face_is_hole", ValueType.BOOL, VariableNode("face", ValueType.FACE)),
                    ),
                    RenderNode(
                        call("canvas_from_grid", ValueType.CANVAS, grid),
                        holes_v,
                        call("object_color", ValueType.COLOR, reference_v),
                        "paint",
                    ),
                ),
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


def pack_objects_by_area_program(*, axis: str = "row") -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    objects_v = VariableNode("objects", ValueType.OBJECT_SET)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "objects",
            call("foreground_objects", ValueType.OBJECT_SET, scene_v),
            PackNode(
                SortNode(
                    objects_v,
                    "item",
                    call("object_area", ValueType.SCALAR, VariableNode("item", ValueType.OBJECT)),
                    descending=True,
                ),
                call("background_color", ValueType.COLOR, scene_v),
                axis=axis,
                gap=1,
                normalize=True,
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


def foreground_dilation_closure_program(*, fill_color: int = 2) -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    closure_v = VariableNode("closure", ValueType.MASK)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "closure",
            RepeatUntilStableNode(
                call("foreground_mask", ValueType.MASK, scene_v),
                "state",
                call("mask_dilate4", ValueType.MASK, VariableNode("state", ValueType.MASK)),
                maximum_steps=120,
                monotone=True,
            ),
            RenderNode(
                call(
                    "blank_canvas_like",
                    ValueType.CANVAS,
                    grid,
                    call("background_color", ValueType.COLOR, scene_v),
                ),
                closure_v,
                LiteralNode(ValueType.COLOR, int(fill_color)),
                "paint",
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


def single_object_identity_else_pack_program() -> Program:
    grid = InputNode("input", ValueType.GRID)
    scene_v = VariableNode("scene", ValueType.SCENE)
    objects_v = VariableNode("objects", ValueType.OBJECT_SET)
    root = LetNode(
        "scene",
        call("analyze", ValueType.SCENE, grid),
        LetNode(
            "objects",
            call("foreground_objects", ValueType.OBJECT_SET, scene_v),
            IfNode(
                call(
                    "integer_equal",
                    ValueType.BOOL,
                    call("object_set_count", ValueType.INTEGER, objects_v),
                    LiteralNode(ValueType.INTEGER, 1),
                ),
                grid,
                PackNode(
                    objects_v,
                    call("background_color", ValueType.COLOR, scene_v),
                    axis="row",
                    gap=0,
                ),
            ),
        ),
    )
    return Program((InputSpec("input", ValueType.GRID),), root)


__all__ = [
    "fill_holes_with_smallest_object_color_program",
    "foreground_dilation_closure_program",
    "pack_objects_by_area_program",
    "recolor_all_objects_to_smallest_color_program",
    "recolor_largest_with_smallest_color_program",
    "single_object_identity_else_pack_program",
]
