"""Obstruction-guided finite macro-sketch synthesis."""
from __future__ import annotations

import time
from typing import Any, Mapping

from komorebi_lasm_compiler.common import equal, training_hashes
from komorebi_lasm_compiler.model import canonical_json, sha256_record

from .families import DEFINITIONS, execute_family
from .ir_bridge import execute_via_ir, to_ir_program
from .model import CandidateExecution, SynthesizedProgram, SynthesisTrace
from .obstruction import derive_obstruction_packet


def _hole_search_size(definition: Any) -> int:
    size = 1
    for hole in definition.sketch.holes:
        size *= max(1, len(hole.domain))
    return size


def eligible_definitions(packet: Any) -> tuple[Any, ...]:
    lanes = set(packet.route_lanes)
    return tuple(definition for definition in DEFINITIONS if lanes.intersection(definition.lanes))


def compile_programs(task: Mapping[str, Any]) -> tuple[list[SynthesizedProgram], SynthesisTrace, Any]:
    started = time.perf_counter()
    packet = derive_obstruction_packet(task)
    trace = SynthesisTrace(obstruction_packet_id=packet.packet_id)
    programs: list[SynthesizedProgram] = []
    hashes = training_hashes(task)
    seen = set()
    for definition in eligible_definitions(packet):
        trace.lanes_attempted.append(definition.name)
        trace.sketches_considered += 1
        trace.hole_assignments_considered += _hole_search_size(definition)
        try:
            assignments = definition.compiler(task)
        except Exception:
            assignments = []
        for parameters in assignments:
            signature = (definition.name, canonical_json(parameters))
            if signature in seen:
                continue
            seen.add(signature)
            try:
                if not all(equal(definition.executor(example["input"], parameters), example["output"]) for example in task.get("train", ())):
                    continue
            except Exception:
                continue
            trace.exact_training_programs += 1
            programs.append(SynthesizedProgram(
                family=definition.name,
                macro_schema=definition.macro_schema,
                sketch_id=definition.sketch.sketch_id,
                parameters=dict(parameters),
                cost=definition.sketch.cost,
                training_hashes=hashes,
                description=definition.sketch.description,
            ))
    programs.sort(key=lambda program: (program.cost, program.macro_schema, program.family, program.signature_hash))
    trace.elapsed_seconds = 0.0
    return programs, trace, packet


def execute_candidates(task: Mapping[str, Any]) -> tuple[list[CandidateExecution], SynthesisTrace, Any]:
    programs, trace, packet = compile_programs(task)
    by_behavior: dict[tuple[tuple[tuple[int, ...], ...], ...], CandidateExecution] = {}
    for program in programs:
        direct_outputs = []
        try:
            for example in task.get("test", ()):
                grid = example["input"]  # attached test outputs are intentionally ignored
                direct = execute_family(program.family, grid, program.parameters)
                via_ir = execute_via_ir(program, grid)
                if direct != via_ir:
                    raise AssertionError("native and Program IR v2 executions disagree")
                direct_outputs.append(direct)
        except Exception:
            trace.runtime_rejections += 1
            continue
        outputs = tuple(direct_outputs)
        candidate = CandidateExecution(
            program=program,
            outputs=outputs,
            ir_program_hash=to_ir_program(program).content_hash(),
            direct_execution_hash=sha256_record(outputs),
        )
        current = by_behavior.get(outputs)
        if current is None or (program.cost, program.signature_hash) < (current.program.cost, current.program.signature_hash):
            by_behavior[outputs] = candidate
    result = sorted(by_behavior.values(), key=lambda candidate: (candidate.program.cost, candidate.program.macro_schema, candidate.program.signature_hash))
    trace.behavior_classes = len(result)
    return result, trace, packet


def compile_record(task: Mapping[str, Any]) -> dict[str, Any]:
    candidates, trace, packet = execute_candidates(task)
    return {
        "schema": "komorebi.lasm_obstruction_guided_macro_compilation",
        "schema_version": 1,
        "obstruction": packet.to_record(),
        "trace": trace.to_record(),
        "candidates": [candidate.to_record() for candidate in candidates],
    }


__all__ = ["compile_programs", "compile_record", "eligible_definitions", "execute_candidates"]
