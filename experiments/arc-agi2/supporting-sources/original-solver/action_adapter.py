"""Pure compilation functions extracted unchanged from the Block 10 audit.
No scoring imports or solution access. Author: Komorebi P.
"""
from __future__ import annotations
from typing import Any, Mapping, Sequence
from komorebi_lasm_composition.model import canonical_value, sha256_record, validate_grid
from komorebi_lasm_action.targeted import compile_targeted_tools_traced
from komorebi_lasm_action.tools import synthesize_complete_scene_native_tools
SCHEMA_VERSION = 1

def _test_inputs(task: Mapping[str, Any]) -> tuple[Any, ...]:
    tests = task.get("test")
    if not isinstance(tests, Sequence) or isinstance(tests, (str, bytes, bytearray)):
        raise TypeError("task test examples must be a sequence")
    return tuple(validate_grid(example["input"]) for example in tests)

def obstruction_route_eligible(block9_record: Mapping[str, Any]) -> bool:
    """Select a frozen Block 9 failure mode without consulting a test label."""

    if block9_record.get("error"):
        return False
    trace = block9_record.get("trace")
    if not isinstance(trace, Mapping):
        return False
    transitions = trace.get("transitions_accepted", 0)
    exact_programs = trace.get("exact_programs", 0)
    return (
        isinstance(transitions, int)
        and not isinstance(transitions, bool)
        and transitions == 0
        and isinstance(exact_programs, int)
        and not isinstance(exact_programs, bool)
        and exact_programs == 0
    )

def _semantic_mechanism(program: Any) -> str:
    return "semantic:" + ":".join(program.grammar_word)

def _targeted_mechanism(program: Any) -> str:
    return f"targeted:{program.family}"

def _add_behavior(
    groups: dict[str, dict[str, Any]],
    outputs: tuple[Any, ...],
    mechanism: Mapping[str, Any],
) -> None:
    behavior_hash = sha256_record(outputs)
    entry = groups.setdefault(
        behavior_hash,
        {
            "behavior_hash": behavior_hash,
            "test_predictions": canonical_value(outputs),
            "mechanisms": [],
        },
    )
    identity = sha256_record(mechanism)
    known = {sha256_record(item) for item in entry["mechanisms"]}
    if identity not in known:
        entry["mechanisms"].append(canonical_value(mechanism))

def compile_action_record(
    task_id: str,
    task: Mapping[str, Any],
    block9_record: Mapping[str, Any],
    *,
    semantic_limits: ToolSynthesisLimits | None = None,
) -> dict[str, Any]:
    """Compile one label-blind overlay record from a public challenge row."""

    eligible = obstruction_route_eligible(block9_record)
    base: dict[str, Any] = {
        "schema": "komorebi.lasm_action.task_compile_record",
        "schema_version": SCHEMA_VERSION,
        "task_id": str(task_id),
        "route": "block9_zero_transition" if eligible else "frozen_block9_fallback",
        "route_eligible": eligible,
        "candidates": [],
        "selected_behavior_hash": "",
        "unique_test_behavior": False,
        "semantic_trace": {
            "programs_considered": 0,
            "executions_performed": 0,
            "exact_programs": 0,
            "behavior_classes": 0,
            "limit_reached": "",
            "escalated": False,
            "complete": True,
        },
        "targeted_trace": {
            "exact_programs": 0,
            "programs_considered": 0,
            "demonstration_executions": 0,
            "test_executions": 0,
            "limit_reached": "",
        },
        "error": None,
    }
    if not eligible:
        base["content_hash"] = sha256_record(base)
        return base

    try:
        test_inputs = _test_inputs(task)
        groups: dict[str, dict[str, Any]] = {}

        targeted_result = compile_targeted_tools_traced(task)
        targeted = targeted_result.programs
        targeted_executions = 0
        for program in targeted:
            try:
                predictions = tuple(program.execute(grid) for grid in test_inputs)
                targeted_executions += len(test_inputs)
            except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
                continue
            _add_behavior(
                groups,
                predictions,
                {
                    "lane": "targeted",
                    "mechanism_key": _targeted_mechanism(program),
                    "program": program.to_record(),
                },
            )
        base["targeted_trace"] = {
            "exact_programs": len(targeted),
            "programs_considered": targeted_result.programs_considered,
            "demonstration_executions": targeted_result.executions_performed,
            "test_executions": targeted_executions,
            "limit_reached": targeted_result.limit_reached,
        }

        # Only the named, exhaustively enumerated subgrammar can authorize a
        # semantic prediction.  The broader bounded grammar remains a
        # diagnostic API and fails closed on every enumeration limit.
        del semantic_limits
        semantic = synthesize_complete_scene_native_tools(task)
        complete = semantic.complete
        base["semantic_trace"] = {
            "programs_considered": semantic.certificate.programs_enumerated,
            "executions_performed": semantic.executions_performed,
            "exact_programs": semantic.exact_programs if complete else 0,
            "behavior_classes": semantic.behavior_classes if complete else 0,
            "limit_reached": "",
            "route": semantic.certificate.route,
            "program_space_hash": semantic.certificate.program_space_hash,
            "completion_certificate": semantic.certificate.to_record(),
            "escalated": False,
            "complete": complete,
        }
        if complete:
            for candidate in semantic.candidates:
                _add_behavior(
                    groups,
                    candidate.test_outputs,
                    {
                        "lane": "semantic",
                        "mechanism_key": _semantic_mechanism(candidate.program),
                        "program": candidate.program.to_record(),
                    },
                )
        candidates = []
        for behavior_hash in sorted(groups):
            item = groups[behavior_hash]
            item["mechanisms"] = sorted(
                item["mechanisms"],
                key=lambda value: (
                    int(value["program"]["cost"]),
                    value["mechanism_key"],
                    sha256_record(value["program"]),
                ),
            )
            item["content_hash"] = sha256_record(item)
            candidates.append(item)
        base["candidates"] = candidates
        base["unique_test_behavior"] = len(candidates) == 1
        if len(candidates) == 1:
            base["selected_behavior_hash"] = candidates[0]["behavior_hash"]
    except Exception as error:  # retain every failure in the audit ledger
        base["error"] = f"{type(error).__name__}: {error}"
        base["candidates"] = []
        base["unique_test_behavior"] = False
        base["selected_behavior_hash"] = ""
    base["content_hash"] = sha256_record(base)
    return base
