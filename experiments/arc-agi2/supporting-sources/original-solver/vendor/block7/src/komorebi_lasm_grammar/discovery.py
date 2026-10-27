"""Training-only broad activation and macro-guided candidate discovery."""
from __future__ import annotations

import copy
from dataclasses import replace
from typing import Any, Callable, Mapping, Sequence

from komorebi_lasm_compiler.common import equal, freeze, training_hashes
from komorebi_lasm_compiler.compiler import route_task
from komorebi_lasm_compiler.execution import execute_compiled
from komorebi_lasm_compiler.ir_bridge import execute_via_ir, to_ir_program
from komorebi_lasm_compiler.model import CandidateExecution, CompiledProgram, sha256_record
from komorebi_lasm_compiler.targeted import (
    Compiled as TargetedCompiled,
    compile_axis_rank_recolor,
    compile_retain_rectangles,
)

from .model import MacroBank


# Only families with demonstrated route-shadowing or a stable targeted selector are
# expanded outside Block 6's original route.  Structural families are already run
# unconditionally by Block 6 and therefore do not need a second execution path.
_BROAD_COMPILERS: dict[str, Callable[[Mapping[str, Any]], list[TargetedCompiled]]] = {
    "axis_rank_recolor": compile_axis_rank_recolor,
    "retain_maximal_rectangles": compile_retain_rectangles,
}


def candidate_outputs(candidate: Mapping[str, Any]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(freeze(value) for value in candidate.get("outputs", []))


def candidate_signature(candidate: Mapping[str, Any]) -> str:
    return str(candidate["program"]["signature"])


def candidate_family(candidate: Mapping[str, Any]) -> str:
    return str(candidate["program"]["family"])


def candidate_parameters(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return dict(candidate["program"].get("parameters", {}))


def candidate_correct(candidate: Mapping[str, Any], targets: Sequence[Any]) -> bool:
    return candidate_outputs(candidate) == tuple(freeze(value) for value in targets)


def _all_training_exact(program: CompiledProgram, task: Mapping[str, Any]) -> bool:
    try:
        return all(
            freeze(execute_compiled(program.family, example["input"], program.parameters))
            == freeze(example["output"])
            for example in task.get("train", [])
        )
    except Exception:
        return False


def _convert_targeted(task: Mapping[str, Any], value: TargetedCompiled) -> dict[str, Any] | None:
    route = route_task(task)
    program = CompiledProgram(
        family=value.family,
        parameters=dict(value.params),
        cost=4,
        origin="persistent_macro_broad_activation",
        route=route,
        training_hashes=training_hashes(task),
        description=(
            "Training-exact program activated outside the original narrow route by a "
            "previously promoted persistent grammar macro."
        ),
    )
    if not _all_training_exact(program, task):
        return None
    direct_outputs = []
    try:
        for test_example in task.get("test", []):
            # Deliberately access only the input.  Any attached test output is ignored.
            grid = test_example["input"]
            direct = freeze(execute_compiled(program.family, grid, program.parameters))
            via_ir = execute_via_ir(program, grid)
            if direct != via_ir:
                raise AssertionError("direct execution and Program IR v2 execution disagree")
            direct_outputs.append(direct)
    except Exception:
        return None
    ir_program = to_ir_program(program)
    return CandidateExecution(
        program=program,
        outputs=tuple(direct_outputs),
        ir_program_hash=ir_program.content_hash(),
        direct_execution_hash=sha256_record(direct_outputs),
    ).to_record()


def broad_candidates(
    task: Mapping[str, Any],
    *,
    bank: MacroBank | None = None,
    families: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Compile bounded broad candidates using training demonstrations only.

    If ``bank`` is provided, only stable macros in that bank can activate a
    resulting program.  Without a bank, the function is an audit-time discovery
    pass used after labels are revealed to update macro evidence.
    """
    selected = tuple(families) if families is not None else tuple(_BROAD_COMPILERS)
    result: dict[str, dict[str, Any]] = {}
    for family in selected:
        compiler = _BROAD_COMPILERS.get(family)
        if compiler is None:
            continue
        try:
            values = compiler(task)
        except Exception:
            values = []
        for value in values:
            if value.family != family:
                continue
            if bank is not None and not bank.permits(value.family, value.params):
                continue
            record = _convert_targeted(task, value)
            if record is None:
                continue
            signature = candidate_signature(record)
            current = result.get(signature)
            if current is None or int(record["program"]["cost"]) < int(current["program"]["cost"]):
                result[signature] = record
    return sorted(result.values(), key=lambda item: (int(item["program"]["cost"]), candidate_signature(item)))


def expanded_record(
    task: Mapping[str, Any],
    routed_record: Mapping[str, Any],
    *,
    bank: MacroBank | None = None,
    audit_discovery: bool = False,
) -> dict[str, Any]:
    """Merge Block 6 candidates with bounded grammar-promoted activations."""
    output = copy.deepcopy(dict(routed_record))
    output.setdefault("candidates", [])
    output.setdefault("error", None)
    trace = dict(output.get("trace", {}))
    seen = {candidate_signature(candidate) for candidate in output["candidates"]}
    additions = broad_candidates(task, bank=None if audit_discovery else bank)
    for candidate in additions:
        if candidate_signature(candidate) not in seen:
            output["candidates"].append(candidate)
            seen.add(candidate_signature(candidate))
    output["candidates"] = sorted(
        output["candidates"],
        key=lambda item: (int(item["program"].get("cost", 0)), candidate_signature(item)),
    )
    trace["block7_broad_candidates"] = len(additions)
    trace["block7_added_candidates"] = len(output["candidates"]) - len(routed_record.get("candidates", []))
    output["trace"] = trace
    return output


def scrub_test_outputs(task: Mapping[str, Any]) -> dict[str, Any]:
    """Return a copy whose test examples contain input only."""
    clean = copy.deepcopy(dict(task))
    clean["test"] = [{"input": copy.deepcopy(item["input"])} for item in task.get("test", [])]
    return clean


__all__ = [
    "broad_candidates",
    "candidate_correct",
    "candidate_family",
    "candidate_outputs",
    "candidate_parameters",
    "candidate_signature",
    "expanded_record",
    "scrub_test_outputs",
]
