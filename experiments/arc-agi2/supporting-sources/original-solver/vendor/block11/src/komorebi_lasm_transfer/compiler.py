"""Unified label-blind compiler for PR-LASM Block 11.

Each constituent lane freezes target-free programs, exactly replays every
training demonstration, and materializes test-input behavior independently.
This module performs the final exact-raster quotient across lanes.  Agreement
becomes corroboration; disagreement becomes ambiguity and therefore abstention.

Author: Komorebi P.
"""
from __future__ import annotations

from dataclasses import dataclass
import multiprocessing as mp
import os
from typing import Any, Callable, Iterable, Mapping, Sequence

from komorebi_lasm_composition.model import canonical_value, sha256_record
from komorebi_lasm_composition.task import sanitized_task_mapping

from .action_schemas import compile_action_schemas
from .ambient_topology import compile_ambient_topology
from .residual_composition import (
    compile_residual_composition,
    residual_composition_route,
)
from .shape_layout import PromotionPolicy, compile_shape_layout
from .tournament import quotient_behaviors


SCHEMA_VERSION = 1
TRANSFER_SCHEMA = "komorebi.lasm_transfer.task_compile_record"
MAX_CORPUS_WORKERS = 32


def _training_shapes(task: Mapping[str, Any]) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    result = []
    for example in task.get("train", ()):
        source = example["input"]
        target = example["output"]
        result.append(((len(source), len(source[0])), (len(target), len(target[0]))))
    return tuple(result)


def transfer_route_eligible(block10_record: Mapping[str, Any]) -> bool:
    """Return the inherited zero-transition action-schema route."""

    return (
        block10_record.get("route_eligible") is True
        and not block10_record.get("candidates")
        and not block10_record.get("error")
    )


@dataclass(frozen=True, slots=True)
class ExternalLaneBehavior:
    """Target-free adapter for an independently compiled Block 11 lane."""

    lane: str
    predictions: tuple[Any, ...]
    mechanism: Mapping[str, Any]


ExternalCompiler = Callable[[Mapping[str, Any]], tuple[ExternalLaneBehavior, ...]]


def compile_transfer_task(
    task_id: str,
    task: Mapping[str, Any],
    block10_record: Mapping[str, Any],
    *,
    allow_provisional_action: bool = False,
    allow_provisional_shape: bool = False,
    allow_provisional_residual: bool = False,
    allow_provisional_ambient: bool = False,
    external_compilers: Sequence[ExternalCompiler] = (),
) -> dict[str, Any]:
    """Compile one task without any access to its held-out answer.

    ``external_compilers`` is an experimentation hook.  Inputs are sanitized,
    but the hook's completeness and replay claims are caller-trusted; the
    release corpus compiler never accepts or invokes external hooks.
    """

    for name, value in (
        ("allow_provisional_action", allow_provisional_action),
        ("allow_provisional_shape", allow_provisional_shape),
        ("allow_provisional_residual", allow_provisional_residual),
        ("allow_provisional_ambient", allow_provisional_ambient),
    ):
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be Boolean")
    try:
        # Establish one structural label boundary before routing or invoking
        # any lane. External adapters never receive the caller's raw test
        # records and cannot observe an attached ``output``.
        safe_task = sanitized_task_mapping(task)
        inherited_clear = not block10_record.get("candidates") and not block10_record.get("error")
        action_eligible = transfer_route_eligible(block10_record)
        shape_relations = _training_shapes(safe_task)
        shape_eligible = inherited_clear and any(
            source != target for source, target in shape_relations
        )
        residual_route = inherited_clear and residual_composition_route(safe_task)
        ambient_route = (
            inherited_clear
            and bool(shape_relations)
            and all(source == target for source, target in shape_relations)
            and any(
                example["input"] != example["output"]
                for example in safe_task["train"]
            )
        )
    except Exception as error:
        failed: dict[str, Any] = {
            "schema": TRANSFER_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "task_id": str(task_id),
            "route_eligible": False,
            "route": "compiler_input_error",
            "eligible_lanes": [],
            "active_lanes": [],
            "training_shape_relations": [],
            "lanes": {},
            "candidates": [],
            "unique_test_behavior": False,
            "selected_behavior_hash": "",
            "error": f"{type(error).__name__}: {error}",
        }
        failed["content_hash"] = sha256_record(failed)
        return canonical_value(failed)
    residual_eligible = residual_route and allow_provisional_residual
    external_eligible = inherited_clear and bool(external_compilers)
    eligible = (
        action_eligible or shape_eligible or residual_route
        or ambient_route or external_eligible
    )
    eligible_lanes = [
        name for name, active in (
            ("action_schema", action_eligible),
            ("shape_layout", shape_eligible),
            ("residual_composition", residual_route),
            ("ambient_topology", ambient_route),
            ("external", external_eligible),
        )
        if active
    ]
    active_lanes = [
        name for name, active in (
            ("action_schema", action_eligible),
            ("shape_layout", shape_eligible),
            ("residual_composition", residual_eligible),
            ("ambient_topology", ambient_route),
            ("external", external_eligible),
        )
        if active
    ]
    base: dict[str, Any] = {
        "schema": TRANSFER_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": str(task_id),
        "route_eligible": eligible,
        "route": "block11_training_obstruction" if eligible else "frozen_block10_fallback",
        "eligible_lanes": eligible_lanes,
        "active_lanes": active_lanes,
        "training_shape_relations": [
            {"input": list(source), "output": list(target)}
            for source, target in shape_relations
        ],
        "lanes": {},
        "candidates": [],
        "unique_test_behavior": False,
        "selected_behavior_hash": "",
        "error": None,
    }
    if not eligible:
        base["content_hash"] = sha256_record(base)
        return canonical_value(base)

    lane_behaviors: list[tuple[str, Sequence[Any], Mapping[str, Any]]] = []
    try:
        if action_eligible:
            action = compile_action_schemas(
                safe_task, allow_provisional=allow_provisional_action,
            )
            action_record = action.to_record()
            # The full behavior payload is represented once in the final quotient;
            # the lane trace keeps the executable and completeness certificates.
            base["lanes"]["action_schema"] = {
                "receipt": action_record["receipt"],
                "behavior_classes": len(action.behaviors),
                "complete": bool(action.receipt.enumeration_complete),
            }
            if action.receipt.enumeration_complete:
                for behavior in action.behaviors:
                    lane_behaviors.append((
                        "action_schema",
                        behavior.outputs,
                        {
                            "schema_keys": list(behavior.schemas),
                            "representative_program": behavior.representative.to_record(),
                            "equivalent_program_ids_hash": sha256_record(
                                behavior.equivalent_program_ids
                            ),
                            "equivalent_programs": len(behavior.equivalent_program_ids),
                        },
                    ))
        else:
            base["lanes"]["action_schema"] = {"routed": False}

        shape_policy = PromotionPolicy(
            allow_stable=True,
            allow_provisional_periodic=allow_provisional_shape,
        )
        if shape_eligible:
            shape = compile_shape_layout(safe_task, policy=shape_policy)
            shape_record = shape.to_record()
            base["lanes"]["shape_layout"] = {
                "trace": shape_record["trace"],
                "promotion_policy_id": shape.policy_id,
                "behavior_classes": len(shape.behaviors),
                "complete": bool(shape.trace.complete),
            }
            if shape.trace.complete:
                for behavior in shape.behaviors:
                    lane_behaviors.append((
                        "shape_layout",
                        behavior.predictions,
                        {
                            "schema_keys": sorted({program.family for program in behavior.programs}),
                            "programs": [program.to_record() for program in behavior.programs],
                            "grammar_contract_hash": shape.trace.grammar_contract_hash,
                        },
                    ))
        else:
            base["lanes"]["shape_layout"] = {"routed": False}

        if residual_eligible:
            residual = compile_residual_composition(safe_task)
            residual_record = residual.to_record()
            base["lanes"]["residual_composition"] = {
                "receipt": residual_record["receipt"],
                "behavior_classes": len(residual.behaviors),
                "complete": bool(residual.receipt.enumeration_complete),
                "status": residual.status,
                "promotion_status": "provisional",
            }
            if residual.receipt.enumeration_complete:
                for behavior in residual.behaviors:
                    word_schema = list(behavior.representative.word_schema)
                    lane_behaviors.append((
                        "residual_composition",
                        behavior.predictions,
                        {
                            "schema_keys": [" -> ".join(word_schema)],
                            "word_schema": word_schema,
                            "representative_program": behavior.representative.to_record(),
                            "equivalent_program_ids_hash": sha256_record(
                                behavior.equivalent_program_ids
                            ),
                            "equivalent_programs": len(behavior.equivalent_program_ids),
                            "receipt_hash": residual.receipt.receipt_hash,
                            "enumeration_complete": True,
                            "promotion_status": "provisional",
                        },
                    ))
        else:
            base["lanes"]["residual_composition"] = {
                "routed": bool(residual_route),
                "active": False,
                "policy": (
                    "provisional_disabled" if residual_route else "not_structurally_eligible"
                ),
            }

        if ambient_route:
            ambient = compile_ambient_topology(
                safe_task, allow_provisional=allow_provisional_ambient,
            )
            ambient_record = ambient.to_record()
            base["lanes"]["ambient_topology"] = {
                "receipt": ambient_record["receipt"],
                "behavior_classes": len(ambient.behaviors),
                "complete": bool(ambient.receipt.complete),
                "status": ambient.status,
                "policy_hash": ambient.policy_hash,
                "provisional_admitted": allow_provisional_ambient,
            }
            if ambient.receipt.complete:
                for behavior in ambient.behaviors:
                    families = sorted({program.operator for program in behavior.programs})
                    lane_behaviors.append((
                        "ambient_topology",
                        behavior.predictions,
                        {
                            "schema_keys": families,
                            "representative_program": behavior.representative.to_record(),
                            "equivalent_program_ids_hash": sha256_record(
                                behavior.equivalent_program_ids
                            ),
                            "equivalent_programs": len(behavior.equivalent_program_ids),
                            "grammar_hash": ambient.receipt.grammar_hash,
                            "complete": True,
                        },
                    ))
        else:
            base["lanes"]["ambient_topology"] = {"routed": False}

        external_records = []
        for compiler in external_compilers:
            values = compiler(safe_task)
            for value in values:
                lane_behaviors.append((value.lane, value.predictions, value.mechanism))
            external_records.append({
                "compiler": getattr(compiler, "__name__", type(compiler).__name__),
                "behaviors": len(values),
            })
        if external_records:
            base["lanes"]["external"] = {
                "trust_boundary": "caller_supplied_experiment_not_release_corpus",
                "compilers": external_records,
            }

        expected_arity = len(safe_task["test"])
        if any(len(predictions) != expected_arity for _, predictions, _ in lane_behaviors):
            raise ValueError("candidate prediction arity disagrees with sanitized test inputs")
        candidates = quotient_behaviors(lane_behaviors)
        base["candidates"] = list(candidates)
        base["unique_test_behavior"] = len(candidates) == 1
        if len(candidates) == 1:
            base["selected_behavior_hash"] = candidates[0]["behavior_hash"]
    except Exception as error:  # every task failure remains explicit and fail-closed
        base["error"] = f"{type(error).__name__}: {error}"
        base["candidates"] = []
        base["unique_test_behavior"] = False
        base["selected_behavior_hash"] = ""
    base["content_hash"] = sha256_record(base)
    return canonical_value(base)


def _worker(
    payload: tuple[str, Mapping[str, Any], Mapping[str, Any], bool, bool, bool, bool],
) -> tuple[str, dict[str, Any]]:
    (
        task_id,
        task,
        block10_record,
        allow_provisional_action,
        allow_provisional_shape,
        allow_provisional_residual,
        allow_provisional_ambient,
    ) = payload
    return task_id, compile_transfer_task(
        task_id,
        task,
        block10_record,
        allow_provisional_action=allow_provisional_action,
        allow_provisional_shape=allow_provisional_shape,
        allow_provisional_residual=allow_provisional_residual,
        allow_provisional_ambient=allow_provisional_ambient,
    )


def compile_transfer_corpus(
    challenges: Mapping[str, Any],
    block10_records: Mapping[str, Any],
    *,
    workers: int = 1,
    allow_provisional_action: bool = False,
    allow_provisional_shape: bool = False,
    allow_provisional_residual: bool = False,
    allow_provisional_ambient: bool = False,
) -> dict[str, Any]:
    """Freeze the complete built-in corpus without accepting a score stream."""

    if set(challenges) != set(block10_records):
        raise ValueError("challenge and Block 10 task sets differ")
    if (
        isinstance(workers, bool)
        or not isinstance(workers, int)
        or workers < 1
        or workers > MAX_CORPUS_WORKERS
    ):
        raise ValueError(f"workers must be an integer from 1 to {MAX_CORPUS_WORKERS}")
    items = tuple(
        (
            task_id,
            challenges[task_id],
            block10_records[task_id],
            allow_provisional_action,
            allow_provisional_shape,
            allow_provisional_residual,
            allow_provisional_ambient,
        )
        for task_id in sorted(challenges)
    )
    records: dict[str, Any] = {}
    if workers == 1:
        iterator = map(_worker, items)
        pool = None
    else:
        context = mp.get_context("spawn" if os.name == "nt" else "fork")
        pool = context.Pool(processes=workers, maxtasksperchild=32)
        iterator = pool.imap_unordered(_worker, items, chunksize=2)
    try:
        for task_id, record in iterator:
            records[task_id] = record
    except BaseException:
        if pool is not None:
            pool.terminate()
            pool.join()
        raise
    else:
        if pool is not None:
            pool.close()
            pool.join()
    if len(records) != len(items):
        raise RuntimeError("corpus compilation returned an incomplete task set")
    return {task_id: records[task_id] for task_id in sorted(records)}


__all__ = [
    "ExternalCompiler",
    "ExternalLaneBehavior",
    "MAX_CORPUS_WORKERS",
    "SCHEMA_VERSION",
    "TRANSFER_SCHEMA",
    "compile_transfer_corpus",
    "compile_transfer_task",
    "transfer_route_eligible",
]
