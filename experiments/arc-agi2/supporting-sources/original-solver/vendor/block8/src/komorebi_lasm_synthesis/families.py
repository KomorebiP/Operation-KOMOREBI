"""Registry of finite obstruction-guided macro sketches."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

import numpy as np

from komorebi_lasm_compiler.common import equal, freeze

from . import families_clear as clear
from . import families_key as key
from . import families_periodic as periodic
from . import families_seeded as seeded
from . import families_semantic as semantic
from .model import HoleSpec, MacroSketch

Compiler = Callable[[Mapping[str, Any]], list[dict[str, Any]]]
Executor = Callable[[Any, Mapping[str, Any]], Any]


@dataclass(frozen=True)
class FamilyDefinition:
    name: str
    macro_schema: str
    lanes: tuple[str, ...]
    compiler: Compiler
    executor: Executor
    sketch: MacroSketch


def _parameters_from_pairs(values: list[tuple[str, dict[str, Any]]], family: str) -> list[dict[str, Any]]:
    return [dict(parameters) for name, parameters in values if name == family]


def _compile_periodic(task: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not task.get("train"):
        return []
    try:
        for example in task["train"]:
            source = np.asarray(example["input"])
            target = np.asarray(example["output"])
            if source.shape != target.shape or np.array_equal(source, target):
                return []
            output, _ = periodic.execute(example["input"])
            if output != freeze(example["output"]):
                return []
    except Exception:
        return []
    return [{}]


def _execute_periodic(grid: Any, parameters: Mapping[str, Any]) -> Any:
    return periodic.execute(grid)[0]


def _sketch(
    name: str,
    schema: str,
    holes: tuple[HoleSpec, ...],
    kinds: tuple[str, ...],
    cost: int,
    description: str,
) -> MacroSketch:
    return MacroSketch(
        name=name,
        schema=schema,
        family=name,
        holes=holes,
        obstruction_kinds=kinds,
        cost=cost,
        description=description,
    )


DEFINITIONS: tuple[FamilyDefinition, ...] = (
    FamilyDefinition(
        "axis_voronoi_frame", "axis_partition_render",
        ("same_shape_relational", "support_completion"),
        lambda task: _parameters_from_pairs(clear.compile_voronoi(task), "axis_voronoi_frame"),
        clear.exec_voronoi_frame,
        _sketch(
            "axis_voronoi_frame", "axis_partition_render",
            (
                HoleSpec("axis", "direction", ("row", "col"), "finite_semantic_domain"),
                HoleSpec("tie", "symbol", ("low", "high"), "finite_semantic_domain"),
                HoleSpec("full_boundary", "bool", (True, False), "finite_semantic_domain"),
            ),
            ("support_add",), 4,
            "Partition a frame by nearest singleton-marker coordinate.",
        ),
    ),
    FamilyDefinition(
        "plus_stamp_closure", "stencil_completion",
        ("finite_closure", "support_completion"),
        lambda task: _parameters_from_pairs(clear.compile_plus(task), "plus_stamp_closure"),
        clear.exec_plus_stamp,
        _sketch(
            "plus_stamp_closure", "stencil_completion",
            (
                HoleSpec("radius", "integer", (2, 3, 4, 5), "finite_radius_domain"),
                HoleSpec("cross", "bool", (True, False), "finite_kernel_domain"),
                HoleSpec("diag", "bool", (True, False), "finite_kernel_domain"),
            ),
            ("support_add",), 4,
            "Complete disjoint plus seeds with a finite colored stencil.",
        ),
    ),
    FamilyDefinition(
        "cross_intersection_halo", "stencil_completion",
        ("finite_closure", "support_completion"),
        lambda task: _parameters_from_pairs(semantic.compile_cross_halo(task), "cross_intersection_halo"),
        semantic.exec_cross_halo,
        _sketch(
            "cross_intersection_halo", "stencil_completion",
            (HoleSpec("color", "color", ("training_output_novel_color",), "training_output_role"),),
            ("support_add",), 3,
            "Paint the Moore-neighborhood halo of a unique orthogonal-line intersection.",
        ),
    ),
    FamilyDefinition(
        "role_manhattan_connector", "orthogonal_path_constructor",
        ("same_shape_relational", "support_completion"),
        lambda task: _parameters_from_pairs(clear.compile_manhattan(task), "role_manhattan_connector"),
        clear.exec_manhattan,
        _sketch(
            "role_manhattan_connector", "orthogonal_path_constructor",
            (
                HoleSpec("pivot_color", "color_role", ("singleton_marker_role",), "training_input_role"),
                HoleSpec("fill_color", "color", ("training_output_novel_color",), "training_output_role"),
                HoleSpec("routes", "relation_set", ("hv", "vh"), "finite_path_domain"),
            ),
            ("support_add",), 5,
            "Connect role-bound singleton markers through ordered Manhattan paths.",
        ),
    ),
    FamilyDefinition(
        "rectangular_lattice_corridors", "lattice_gap_transport",
        ("ambient_construction", "support_completion"),
        lambda task: _parameters_from_pairs(clear.compile_lattice(task), "rectangular_lattice_corridors"),
        clear.exec_lattice,
        _sketch(
            "rectangular_lattice_corridors", "lattice_gap_transport",
            (
                HoleSpec("bridge", "color", ("training_output_novel_color",), "training_output_role"),
                HoleSpec("terminal", "color", ("training_output_novel_color",), "training_output_role"),
            ),
            ("support_add",), 5,
            "Fill internal and exterior corridors of a complete rectangle lattice.",
        ),
    ),
    FamilyDefinition(
        "periodic_consensus_restore", "periodic_consensus_projection",
        ("periodic_projection",), _compile_periodic, _execute_periodic,
        _sketch(
            "periodic_consensus_restore", "periodic_consensus_projection", (),
            ("mixed", "support_add", "recolor"), 6,
            "Project a noisy repeated field onto its minimum-repair primitive periodic model.",
        ),
    ),
    FamilyDefinition(
        "blank_to_constant_frame", "frame_render",
        ("support_completion",),
        lambda task: _parameters_from_pairs(semantic.compile_blank_frame(task), "blank_to_constant_frame"),
        semantic.exec_blank_frame,
        _sketch(
            "blank_to_constant_frame", "frame_render",
            (HoleSpec("color", "color", ("training_output_novel_color",), "training_output_role"),),
            ("support_add",), 2,
            "Render a constant frame on a blank canvas.",
        ),
    ),
    FamilyDefinition(
        "singleton_to_frame", "frame_render",
        ("support_completion",),
        lambda task: _parameters_from_pairs(semantic.compile_singleton_frame(task), "singleton_to_frame"),
        semantic.exec_singleton_frame,
        _sketch(
            "singleton_to_frame", "frame_render", (), ("support_mixed",), 2,
            "Transport a singleton marker color to the canvas frame.",
        ),
    ),
    FamilyDefinition(
        "rowwise_shear_relaxation", "shear_relaxation",
        ("same_shape_relational",),
        lambda task: _parameters_from_pairs(semantic.compile_shear(task), "rowwise_shear_relaxation"),
        semantic.execute_shear,
        _sketch(
            "rowwise_shear_relaxation", "shear_relaxation",
            (
                HoleSpec("axis", "direction", ("rows", "cols"), "finite_semantic_domain"),
                HoleSpec("anchor", "symbol", ("low", "high"), "finite_semantic_domain"),
                HoleSpec("direction", "symbol", ("toward_anchor", "away"), "finite_semantic_domain"),
            ),
            ("support_mixed",), 4,
            "Relax monochrome row or column spans toward a selected endpoint anchor.",
        ),
    ),
    FamilyDefinition(
        "seeded_component_interior_recolor", "seeded_interior_recolor",
        ("role_rebinding",),
        lambda task: _parameters_from_pairs(seeded.compile(task), "seeded_component_interior_recolor"),
        seeded.execute,
        _sketch(
            "seeded_component_interior_recolor", "seeded_interior_recolor", (),
            ("recolor",), 4,
            "Recolor each eroded component interior from its embedded categorical seed.",
        ),
    ),
    FamilyDefinition(
        "d4_key_block_transfer", "d4_key_block_transfer",
        ("role_rebinding", "same_shape_relational"),
        lambda task: _parameters_from_pairs(key.compile(task), "d4_key_block_transfer"),
        key.execute,
        _sketch(
            "d4_key_block_transfer", "d4_key_block_transfer",
            (HoleSpec("transform", "symbol", ("id", "r90", "r180", "r270", "fliplr", "flipud", "transpose", "anti_transpose"), "finite_group_domain"),),
            ("recolor",), 5,
            "Transfer a D4-normalized small key into a large block occupancy graph.",
        ),
    ),
)

DEFINITION_BY_NAME = {definition.name: definition for definition in DEFINITIONS}
SCHEMA_FAMILIES: dict[str, tuple[str, ...]] = {
    schema: tuple(definition.name for definition in DEFINITIONS if definition.macro_schema == schema)
    for schema in sorted({definition.macro_schema for definition in DEFINITIONS})
}


def execute_family(family: str, grid: Any, parameters: Mapping[str, Any]) -> tuple[tuple[int, ...], ...]:
    try:
        definition = DEFINITION_BY_NAME[family]
    except KeyError as error:
        raise ValueError(f"unknown Block 8 macro family {family!r}") from error
    return freeze(definition.executor(grid, parameters))


def family_sketches() -> tuple[MacroSketch, ...]:
    return tuple(definition.sketch for definition in DEFINITIONS)


__all__ = [
    "DEFINITIONS", "DEFINITION_BY_NAME", "FamilyDefinition", "SCHEMA_FAMILIES",
    "execute_family", "family_sketches",
]
