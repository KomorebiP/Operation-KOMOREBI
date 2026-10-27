"""Unified label-blind compiler for PR-LASM Block 12.

Every lane receives a sanitized task, exactly replays its training pairs, and
materializes test-input behavior without access to a test target.  This module
groups all surviving mechanisms by their complete raster behavior.  Agreement
is corroboration; disagreement is ambiguity and therefore abstention.

Author: Komorebi P.
"""
from __future__ import annotations

from collections import defaultdict
import multiprocessing as mp
import os
from typing import Any, Mapping, Sequence

from komorebi_lasm_composition.model import canonical_value, sha256_record
from komorebi_lasm_composition.task import sanitized_task_mapping

from .ambient_recovery import GRAMMAR_HASH as AMBIENT_GRAMMAR_HASH
from .ambient_recovery import compile_ambient_recovery
from .axis_sequence import GRAMMAR_HASH as AXIS_SEQUENCE_GRAMMAR_HASH
from .axis_sequence import compile_axis_sequence
from .local_transition import GRAMMAR_HASH as LOCAL_TRANSITION_GRAMMAR_HASH
from .local_transition import compile_local_transition
from .object_composition import GRAMMAR_HASH as OBJECT_COMPOSITION_GRAMMAR_HASH
from .object_composition import compile_object_composition
from .periodic_lattice import GRAMMAR_HASH as PERIODIC_LATTICE_GRAMMAR_HASH
from .periodic_lattice import compile_periodic_lattice
from .shape_constructors import GRAMMAR_HASH as SHAPE_CONSTRUCTOR_GRAMMAR_HASH
from .shape_constructors import compile_shape_constructors


SCHEMA_VERSION = 2
COMPILATION_SCHEMA = "komorebi.lasm_falsification.task_compile_record"
MAX_CORPUS_WORKERS = 32


def _behavior_record(
    behavior_hash: str,
    predictions: Sequence[Any],
    mechanisms: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(
        (canonical_value(value) for value in mechanisms),
        key=sha256_record,
    )
    return {
        "behavior_hash": behavior_hash,
        "test_predictions": canonical_value(tuple(predictions)),
        "mechanisms": ordered,
        "mechanism_count": len(ordered),
        "mechanism_digest": sha256_record(ordered),
    }


def compile_falsification_task(
    task_id: str,
    task: Mapping[str, Any],
    *,
    allow_provisional_ambient: bool = False,
    allow_provisional_shape: bool = False,
    allow_provisional_singletons: bool = False,
) -> dict[str, Any]:
    """Compile a task under the immutable Block 12 static grammar."""

    for name, value in (
        ("allow_provisional_ambient", allow_provisional_ambient),
        ("allow_provisional_shape", allow_provisional_shape),
        ("allow_provisional_singletons", allow_provisional_singletons),
    ):
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be Boolean")
    try:
        safe_task = sanitized_task_mapping(task)
    except Exception as error:
        record: dict[str, Any] = {
            "schema": COMPILATION_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "task_id": str(task_id),
            "route_eligible": False,
            "active_lanes": [],
            "lanes": {},
            "candidates": [],
            "selection_complete": False,
            "unique_test_behavior": False,
            "selected_behavior_hash": "",
            "error": f"{type(error).__name__}: {error}",
        }
        record["content_hash"] = sha256_record(record)
        return canonical_value(record)

    base: dict[str, Any] = {
        "schema": COMPILATION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "task_id": str(task_id),
        "route_eligible": False,
        "active_lanes": sorted([
            "ambient_recovery",
            "shape_constructors",
            *(
                [
                    "axis_sequence", "local_transition", "object_composition",
                    "periodic_lattice",
                ]
                if allow_provisional_singletons else []
            ),
        ]),
        "lanes": {},
        "candidates": [],
        "selection_complete": True,
        "unique_test_behavior": False,
        "selected_behavior_hash": "",
        "error": None,
    }
    raw_behaviors: list[tuple[str, Sequence[Any], Mapping[str, Any]]] = []
    try:
        ambient = compile_ambient_recovery(
            safe_task,
            allow_provisional=allow_provisional_ambient,
        )
        ambient_record = ambient.to_record()
        base["lanes"]["ambient_recovery"] = {
            "status": ambient.status,
            "complete": ambient.receipt.complete,
            "behavior_classes": len(ambient.behaviors),
            "allow_provisional": allow_provisional_ambient,
            "receipt": ambient_record["receipt"],
        }
        base["route_eligible"] = bool(ambient.receipt.routed)
        base["selection_complete"] = (
            base["selection_complete"] and ambient.receipt.complete
        )
        if ambient.receipt.complete:
            for behavior in ambient.behaviors:
                families = sorted({program.family for program in behavior.programs})
                raw_behaviors.append((
                    "ambient_recovery",
                    behavior.predictions,
                    {
                        "lane": "ambient_recovery",
                        "schema_keys": families,
                        "representative_program": behavior.representative.to_record(),
                        "equivalent_program_ids": [
                            program.program_id for program in behavior.programs
                        ],
                        "grammar_contract_hash": AMBIENT_GRAMMAR_HASH,
                    },
                ))
    except Exception as error:
        base["error"] = f"{type(error).__name__}: {error}"
        base["lanes"]["ambient_recovery"] = {
            "status": "compiler_error",
            "complete": False,
            "behavior_classes": 0,
        }
        base["selection_complete"] = False

    if not allow_provisional_singletons:
        base["lanes"]["object_composition"] = {
            "status": "provisional_disabled",
            "complete": True,
            "behavior_classes": 0,
        }
    else:
        try:
            composition = compile_object_composition(safe_task)
            composition_record = composition.to_record()
            base["lanes"]["object_composition"] = {
                "status": composition.status,
                "routed": composition.routed,
                "complete": composition.complete,
                "behavior_classes": len(composition.behaviors),
                "programs": len(composition.programs),
                "stress_checks": composition.stress_checks,
                "compilation_hash": composition_record["content_hash"],
            }
            base["route_eligible"] = base["route_eligible"] or composition.routed
            base["selection_complete"] = (
                base["selection_complete"] and composition.complete
            )
            if composition.complete:
                for predictions in composition.behaviors:
                    if not composition.programs:
                        raise AssertionError(
                            "object-composition behavior lacks a supporting program"
                        )
                    raw_behaviors.append((
                        "object_composition",
                        predictions,
                        {
                            "lane": "object_composition",
                            "schema_keys": sorted({
                                program.family for program in composition.programs
                            }),
                            "representative_program": (
                                composition.programs[0].to_record()
                            ),
                            "equivalent_program_ids": [
                                program.program_id for program in composition.programs
                            ],
                            "grammar_contract_hash": (
                                OBJECT_COMPOSITION_GRAMMAR_HASH
                            ),
                        },
                    ))
        except Exception as error:
            prior = base.get("error")
            message = f"{type(error).__name__}: {error}"
            base["error"] = (
                message if prior is None
                else f"{prior}; object_composition={message}"
            )
            base["lanes"]["object_composition"] = {
                "status": "compiler_error",
                "complete": False,
                "behavior_classes": 0,
            }
            base["selection_complete"] = False

    if not allow_provisional_singletons:
        base["lanes"]["local_transition"] = {
            "status": "provisional_disabled",
            "complete": True,
            "behavior_classes": 0,
        }
    else:
        try:
            local = compile_local_transition(safe_task)
            local_record = local.to_record()
            base["lanes"]["local_transition"] = {
                "status": "enabled",
                "routed": local.routed,
                "complete": local.complete,
                "behavior_classes": len(local.behaviors),
                "stress_checks": local.stress_checks,
                "compilation_hash": local_record["content_hash"],
            }
            base["route_eligible"] = base["route_eligible"] or local.routed
            base["selection_complete"] = base["selection_complete"] and local.complete
            if local.complete:
                for predictions in local.behaviors:
                    raw_behaviors.append((
                        "local_transition",
                        predictions,
                        {
                            "lane": "local_transition",
                            "schema_keys": sorted({program.family for program in local.programs}),
                            "representative_program": local.programs[0].to_record(),
                            "equivalent_program_ids": [program.program_id for program in local.programs],
                            "grammar_contract_hash": LOCAL_TRANSITION_GRAMMAR_HASH,
                        },
                    ))
        except Exception as error:
            prior = base.get("error")
            message = f"{type(error).__name__}: {error}"
            base["error"] = message if prior is None else f"{prior}; local_transition={message}"
            base["lanes"]["local_transition"] = {
                "status": "compiler_error",
                "complete": False,
                "behavior_classes": 0,
            }
            base["selection_complete"] = False

    try:
        shape = compile_shape_constructors(
            safe_task,
            allow_provisional=allow_provisional_shape,
        )
        shape_record = shape.to_record()
        base["lanes"]["shape_constructors"] = {
            "status": shape.status,
            "complete": shape.receipt.complete,
            "behavior_classes": len(shape.behaviors),
            "allow_provisional": allow_provisional_shape,
            "receipt": shape_record["receipt"],
        }
        base["route_eligible"] = base["route_eligible"] or shape.receipt.routed
        base["selection_complete"] = (
            base["selection_complete"] and shape.receipt.complete
        )
        if shape.receipt.complete:
            for behavior in shape.behaviors:
                raw_behaviors.append((
                    "shape_constructors",
                    behavior.predictions,
                    {
                        "lane": "shape_constructors",
                        "schema_keys": sorted({program.family for program in behavior.programs}),
                        "representative_program": behavior.representative.to_record(),
                        "equivalent_program_ids": [program.program_id for program in behavior.programs],
                        "grammar_contract_hash": SHAPE_CONSTRUCTOR_GRAMMAR_HASH,
                    },
                ))
    except Exception as error:
        prior = base.get("error")
        message = f"{type(error).__name__}: {error}"
        base["error"] = message if prior is None else f"{prior}; shape_constructors={message}"
        base["lanes"]["shape_constructors"] = {
            "status": "compiler_error",
            "complete": False,
            "behavior_classes": 0,
        }
        base["selection_complete"] = False

    if not allow_provisional_singletons:
        base["lanes"]["axis_sequence"] = {
            "status": "provisional_disabled",
            "complete": True,
            "behavior_classes": 0,
        }
    else:
        try:
            axis = compile_axis_sequence(safe_task)
            axis_record = axis.to_record()
            base["lanes"]["axis_sequence"] = {
                "status": "enabled",
                "routed": axis.routed,
                "complete": axis.complete,
                "behavior_classes": len(axis.behaviors),
                "programs": len(axis.programs),
                "stress_checks": axis.stress_checks,
                "demo_order_invariant": axis.demo_order_invariant,
                "compilation_hash": axis_record["content_hash"],
            }
            base["route_eligible"] = base["route_eligible"] or axis.routed
            base["selection_complete"] = base["selection_complete"] and axis.complete
            if axis.complete:
                for predictions, programs in zip(
                    axis.behaviors, axis.behavior_programs, strict=True,
                ):
                    raw_behaviors.append((
                        "axis_sequence",
                        predictions,
                        {
                            "lane": "axis_sequence",
                            "schema_keys": sorted({program.family for program in programs}),
                            "representative_program": programs[0].to_record(),
                            "equivalent_program_ids": [program.program_id for program in programs],
                            "grammar_contract_hash": AXIS_SEQUENCE_GRAMMAR_HASH,
                        },
                    ))
        except Exception as error:
            prior = base.get("error")
            message = f"{type(error).__name__}: {error}"
            base["error"] = message if prior is None else f"{prior}; axis_sequence={message}"
            base["lanes"]["axis_sequence"] = {
                "status": "compiler_error",
                "complete": False,
                "behavior_classes": 0,
            }
            base["selection_complete"] = False

    if not allow_provisional_singletons:
        base["lanes"]["periodic_lattice"] = {
            "status": "provisional_disabled",
            "complete": True,
            "behavior_classes": 0,
        }
    else:
        try:
            periodic = compile_periodic_lattice(safe_task)
            periodic_record = periodic.to_record()
            base["lanes"]["periodic_lattice"] = {
                "status": periodic.status,
                "routed": periodic.routed,
                "complete": periodic.complete,
                "behavior_classes": len(periodic.behaviors),
                "programs": len(periodic.programs),
                "demonstration_executions": periodic.demonstration_executions,
                "execution_rejections": periodic.runtime_failures,
                "compilation_hash": periodic_record["content_hash"],
            }
            base["route_eligible"] = base["route_eligible"] or periodic.routed
            base["selection_complete"] = base["selection_complete"] and periodic.complete
            if periodic.complete:
                for predictions in periodic.behaviors:
                    programs = tuple(
                        program
                        for program in periodic.programs
                        if tuple(program.execute(example["input"]) for example in safe_task["test"])
                        == predictions
                    )
                    if not programs:
                        raise AssertionError("periodic behavior lost all supporting programs")
                    raw_behaviors.append((
                        "periodic_lattice",
                        predictions,
                        {
                            "lane": "periodic_lattice",
                            "schema_keys": sorted({program.family for program in programs}),
                            "representative_program": programs[0].to_record(),
                            "equivalent_program_ids": [program.program_id for program in programs],
                            "grammar_contract_hash": PERIODIC_LATTICE_GRAMMAR_HASH,
                        },
                    ))
        except Exception as error:
            prior = base.get("error")
            message = f"{type(error).__name__}: {error}"
            base["error"] = message if prior is None else f"{prior}; periodic_lattice={message}"
            base["lanes"]["periodic_lattice"] = {
                "status": "compiler_error",
                "complete": False,
                "behavior_classes": 0,
            }
            base["selection_complete"] = False

    groups: dict[str, dict[str, Any]] = {}
    for _, predictions, mechanism in raw_behaviors:
        behavior_hash = sha256_record(canonical_value(tuple(predictions)))
        group = groups.setdefault(
            behavior_hash,
            {"predictions": predictions, "mechanisms": []},
        )
        if canonical_value(tuple(group["predictions"])) != canonical_value(tuple(predictions)):
            raise AssertionError("behavior hash collision")
        group["mechanisms"].append(mechanism)
    base["candidates"] = [
        _behavior_record(
            behavior_hash,
            group["predictions"],
            group["mechanisms"],
        )
        for behavior_hash, group in sorted(groups.items())
    ]
    base["unique_test_behavior"] = (
        base["selection_complete"] and len(base["candidates"]) == 1
    )
    if base["unique_test_behavior"]:
        base["selected_behavior_hash"] = base["candidates"][0]["behavior_hash"]
    base["content_hash"] = sha256_record(base)
    return canonical_value(base)


def _worker(
    payload: tuple[str, Mapping[str, Any], bool, bool, bool],
) -> tuple[str, dict[str, Any]]:
    (
        task_id, task, allow_provisional_ambient, allow_provisional_shape,
        allow_provisional_singletons,
    ) = payload
    return task_id, compile_falsification_task(
        task_id,
        task,
        allow_provisional_ambient=allow_provisional_ambient,
        allow_provisional_shape=allow_provisional_shape,
        allow_provisional_singletons=allow_provisional_singletons,
    )


def compile_falsification_corpus(
    challenges: Mapping[str, Mapping[str, Any]],
    *,
    workers: int = 1,
    allow_provisional_ambient: bool = False,
    allow_provisional_shape: bool = False,
    allow_provisional_singletons: bool = False,
) -> dict[str, Any]:
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= MAX_CORPUS_WORKERS:
        raise ValueError(f"workers must be an integer in [1, {MAX_CORPUS_WORKERS}]")
    items = [
        (
            str(task_id), task, allow_provisional_ambient, allow_provisional_shape,
            allow_provisional_singletons,
        )
        for task_id, task in sorted(challenges.items())
    ]
    if workers == 1:
        results = map(_worker, items)
        pool = None
    else:
        context = mp.get_context("spawn" if os.name == "nt" else "fork")
        pool = context.Pool(processes=workers, maxtasksperchild=100)
        results = pool.imap_unordered(_worker, items, chunksize=4)
    records = {}
    try:
        for task_id, record in results:
            records[task_id] = record
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    return {task_id: records[task_id] for task_id, _, _, _, _ in items}


__all__ = [
    "COMPILATION_SCHEMA",
    "MAX_CORPUS_WORKERS",
    "compile_falsification_corpus",
    "compile_falsification_task",
]
