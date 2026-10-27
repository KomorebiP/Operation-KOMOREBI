"""Delta-routed bidirectional relational program compiler."""
from __future__ import annotations

import hashlib
import json
import time
from collections import Counter, defaultdict
from dataclasses import replace
from typing import Any, Mapping, Sequence

import numpy as np

from komorebi_lasm_ir import derive_task_delta_pattern

from .common import arr, components, freeze, infer_background, training_hashes
from .execution import execute_compiled
from .ir_bridge import execute_via_ir, to_ir_program
from .model import CandidateExecution, CompilationTrace, CompiledProgram, RouteSignature, canonical_json, sha256_record
from .structural import compile_structural
from .targeted import compile_task_routed


def _shape_relation(task: Mapping[str, Any]) -> str:
    values = []
    for example in task.get("train", []):
        source, target = arr(example["input"]), arr(example["output"])
        if source.shape == target.shape:
            values.append("preserve")
        elif target.shape[0] % source.shape[0] == 0 and target.shape[1] % source.shape[1] == 0:
            values.append(f"upscale:{target.shape[0] // source.shape[0]}x{target.shape[1] // source.shape[1]}")
        elif source.shape[0] % target.shape[0] == 0 and source.shape[1] % target.shape[1] == 0:
            values.append(f"downscale:{source.shape[0] // target.shape[0]}x{source.shape[1] // target.shape[1]}")
        else:
            values.append("constructor")
    return values[0] if values and len(set(values)) == 1 else "mixed"


def _support_relation(task: Mapping[str, Any]) -> str:
    relations = []
    for example in task.get("train", []):
        source, target = arr(example["input"]), arr(example["output"])
        if source.shape != target.shape:
            relations.append("shape_change")
            continue
        background = infer_background(source)
        source_support = source != background
        target_support = target != background
        if np.array_equal(source_support, target_support):
            relations.append("same")
        elif not np.any(target_support & ~source_support):
            relations.append("subset")
        elif not np.any(source_support & ~target_support):
            relations.append("superset")
        else:
            relations.append("mixed")
    return relations[0] if relations and len(set(relations)) == 1 else "mixed"


def route_task(task: Mapping[str, Any]) -> RouteSignature:
    shape = _shape_relation(task)
    support = _support_relation(task)
    enabled = ["shape_changing" if shape != "preserve" else "same_shape"]
    if support in {"same", "subset", "superset", "mixed"}:
        enabled.append(f"support_{support}")
    try:
        # Block 5's exact scene graph intentionally constructs all pairwise
        # object and object-face relations.  That is appropriate for compact
        # scenes but super-quadratic on dense checkerboard/noise-like rasters.
        # The compiler does not need those pairwise relations merely to route
        # such tasks, so detect the finite complexity boundary first and retain
        # a training-only raw-delta certificate instead.
        scene_parts = 0
        for example in task.get("train", []):
            for key in ("input", "output"):
                grid = arr(example[key])
                background = infer_background(grid)
                scene_parts += len(components(grid == background, 4))
                for color in set(int(value) for value in grid.ravel()) - {background}:
                    scene_parts += len(components(grid == color, 4))
                if scene_parts > 96:
                    raise RuntimeError("scene relation budget exceeded")
        pattern = derive_task_delta_pattern(task)
        edit_kinds = tuple(pattern.required_edit_kinds)
        pattern_hash = pattern.content_hash()
        enabled.append("block5_delta_pattern")
    except Exception as error:
        # Ambiguous scene decomposition is itself routing evidence.  Preserve a
        # stable hash of the training-only raw delta rather than inventing an
        # object correspondence.
        edit_kinds = (("delta_fallback", 1),)
        pattern_hash = sha256_record({
            "training": [{"input": freeze(e["input"]), "output": freeze(e["output"])} for e in task.get("train", [])],
            "error_type": type(error).__name__,
        })
        enabled.append("raw_delta_fallback")
    return RouteSignature(
        shape_relation=shape,
        support_relation=support,
        edit_kinds=edit_kinds,
        delta_pattern_hash=pattern_hash,
        enabled_lanes=tuple(enabled),
    )


def compile_programs(task: Mapping[str, Any]) -> tuple[list[CompiledProgram], CompilationTrace]:
    started = time.perf_counter()
    route = route_task(task)
    trace = CompilationTrace(route=route)
    programs: list[CompiledProgram] = []
    same_shape = route.shape_relation == "preserve"

    if same_shape:
        targeted, targeted_routes = compile_task_routed(task)
        trace.lanes_attempted.extend(targeted_routes)
        for value in targeted.values():
            programs.append(
                CompiledProgram(
                    family=value.family,
                    parameters=dict(value.params),
                    cost=4,
                    origin="delta_routed_same_shape",
                    description="Same-shape relational program inferred from demonstration deltas.",
                )
            )
    structural, structural_lanes = compile_structural(task, same_shape=same_shape)
    trace.lanes_attempted.extend(structural_lanes)
    programs.extend(structural)
    trace.raw_programs = len(programs)

    hashes = training_hashes(task)
    exact: dict[str, CompiledProgram] = {}
    for program in programs:
        compiled = replace(program, route=route, training_hashes=hashes)
        try:
            if all(freeze(execute_compiled(compiled.family, example["input"], compiled.parameters)) == freeze(example["output"]) for example in task["train"]):
                exact[compiled.signature] = compiled
        except Exception:
            trace.rejected_runtime += 1
    trace.exact_training_programs = len(exact)
    trace.elapsed_seconds = time.perf_counter() - started
    return sorted(exact.values(), key=lambda item: (item.cost, item.signature)), trace


def execute_candidates(task: Mapping[str, Any]) -> tuple[list[CandidateExecution], CompilationTrace]:
    programs, trace = compile_programs(task)
    by_behavior: dict[tuple[tuple[tuple[int, ...], ...], ...], CandidateExecution] = {}
    for program in programs:
        direct_outputs = []
        ir_outputs = []
        try:
            for test_example in task.get("test", []):
                # Test outputs are deliberately ignored even if attached to the record.
                grid = test_example["input"]
                direct = freeze(execute_compiled(program.family, grid, program.parameters))
                via_ir = execute_via_ir(program, grid)
                if direct != via_ir:
                    raise AssertionError("direct and Program IR execution disagree")
                direct_outputs.append(direct)
                ir_outputs.append(via_ir)
        except Exception:
            trace.rejected_runtime += 1
            continue
        outputs = tuple(direct_outputs)
        ir_program = to_ir_program(program)
        candidate = CandidateExecution(
            program=program,
            outputs=outputs,
            ir_program_hash=ir_program.content_hash(),
            direct_execution_hash=sha256_record(direct_outputs),
        )
        current = by_behavior.get(outputs)
        if current is None or (program.cost, program.signature) < (current.program.cost, current.program.signature):
            by_behavior[outputs] = candidate
    result = sorted(by_behavior.values(), key=lambda item: (item.program.cost, item.program.signature))
    trace.behavior_classes = len(result)
    return result, trace


def compile_record(task: Mapping[str, Any]) -> dict[str, Any]:
    candidates, trace = execute_candidates(task)
    return {
        "schema": "komorebi.lasm_bidirectional_compilation",
        "schema_version": 1,
        "trace": trace.to_record(),
        "candidates": [candidate.to_record() for candidate in candidates],
    }
