"""Training-only obstruction diagnosis for finite macro-sketch routing."""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from komorebi_lasm_compiler.common import arr, components, infer_background, training_hashes

from .model import ObstructionKind, ObstructionPacket


def derive_obstruction_packet(task: Mapping[str, Any]) -> ObstructionPacket:
    examples = list(task.get("train", ()))
    if not examples:
        raise ValueError("at least one training demonstration is required")
    shapes: list[str] = []
    kinds: list[str] = []
    added: list[int] = []
    removed: list[int] = []
    recolored: list[int] = []
    input_colors: list[int] = []
    output_colors: list[int] = []
    complexity = 0
    for example in examples:
        source = arr(example["input"])
        target = arr(example["output"])
        input_colors.append(len(set(int(v) for v in source.ravel())))
        output_colors.append(len(set(int(v) for v in target.ravel())))
        bg = infer_background(source)
        complexity += len(components(source != bg, 4)) + len(components(source == bg, 4))
        if source.shape != target.shape:
            shapes.append(f"{source.shape[0]}x{source.shape[1]}->{target.shape[0]}x{target.shape[1]}")
            kinds.append(ObstructionKind.SHAPE_CHANGE.value)
            added.append(int(target.size))
            removed.append(int(source.size))
            recolored.append(0)
            continue
        shapes.append("preserve")
        source_support = source != bg
        target_support = target != bg
        add_count = int(np.count_nonzero(target_support & ~source_support))
        remove_count = int(np.count_nonzero(source_support & ~target_support))
        recolor_count = int(np.count_nonzero((source != target) & source_support & target_support))
        added.append(add_count)
        removed.append(remove_count)
        recolored.append(recolor_count)
        if add_count == remove_count == recolor_count == 0:
            kinds.append(ObstructionKind.IDENTITY.value)
        elif add_count > 0 and remove_count == recolor_count == 0:
            kinds.append(ObstructionKind.SUPPORT_ADD.value)
        elif remove_count > 0 and add_count == recolor_count == 0:
            kinds.append(ObstructionKind.SUPPORT_REMOVE.value)
        elif recolor_count > 0 and add_count == remove_count == 0:
            kinds.append(ObstructionKind.RECOLOR.value)
        elif add_count or remove_count:
            kinds.append(ObstructionKind.SUPPORT_MIXED.value)
        else:
            kinds.append(ObstructionKind.MIXED.value)
    shape_relation = shapes[0] if len(set(shapes)) == 1 else "mixed"
    unique_kinds = tuple(sorted(set(kinds)))
    lanes: list[str] = []
    if shape_relation == "preserve":
        lanes.extend(["same_shape_relational", "finite_closure", "periodic_projection"])
    else:
        lanes.append("shape_constructor")
    if any(value in unique_kinds for value in (ObstructionKind.SUPPORT_ADD.value, ObstructionKind.SUPPORT_MIXED.value)):
        lanes.extend(["support_completion", "ambient_construction"])
    if ObstructionKind.RECOLOR.value in unique_kinds or any(recolored):
        lanes.append("role_rebinding")
    lanes.append("bounded_raw_delta" if complexity > 96 else "relational_scene")
    return ObstructionPacket(
        shape_relation=shape_relation,
        obstruction_kinds=unique_kinds,
        added_cells=tuple(added),
        removed_cells=tuple(removed),
        recolored_cells=tuple(recolored),
        input_color_counts=tuple(input_colors),
        output_color_counts=tuple(output_colors),
        training_pair_hashes=training_hashes(task),
        scene_complexity=int(complexity),
        route_lanes=tuple(dict.fromkeys(lanes)),
    )


__all__ = ["derive_obstruction_packet"]
