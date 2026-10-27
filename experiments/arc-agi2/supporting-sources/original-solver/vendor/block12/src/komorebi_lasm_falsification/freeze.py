"""Freeze the complete Block 12 public-training prediction corpus.

This module accepts no solution path and imports no scoring code.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import time
from typing import Any, Mapping

from komorebi_lasm_composition.model import sha256_record

from .ambient_recovery import GRAMMAR_HASH as AMBIENT_GRAMMAR_HASH
from .axis_sequence import GRAMMAR_HASH as AXIS_SEQUENCE_GRAMMAR_HASH
from .compiler import compile_falsification_corpus
from .io import load_json, sha256_file, write_json
from .local_transition import GRAMMAR_HASH as LOCAL_TRANSITION_GRAMMAR_HASH
from .object_composition import GRAMMAR_HASH as OBJECT_COMPOSITION_GRAMMAR_HASH
from .periodic_lattice import GRAMMAR_HASH as PERIODIC_LATTICE_GRAMMAR_HASH
from .shape_constructors import GRAMMAR_HASH as SHAPE_CONSTRUCTOR_GRAMMAR_HASH


def _work(records: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    ambient_lane: Counter[str] = Counter()
    local_lane: Counter[str] = Counter()
    shape_lane: Counter[str] = Counter()
    axis_lane: Counter[str] = Counter()
    object_lane: Counter[str] = Counter()
    periodic_lane: Counter[str] = Counter()
    for record in records.values():
        totals["tasks"] += 1
        totals["route_eligible_tasks"] += int(bool(record["route_eligible"]))
        totals["compiler_errors"] += int(bool(record["error"]))
        totals["tasks_with_candidates"] += int(bool(record["candidates"]))
        totals["unique_behavior_tasks"] += int(bool(record["unique_test_behavior"]))
        totals["ambiguous_tasks"] += int(len(record["candidates"]) > 1)
        totals["selection_incomplete_tasks"] += int(
            not bool(record.get("selection_complete"))
        )
        ambient = record["lanes"].get("ambient_recovery", {})
        receipt = ambient.get("receipt", {})
        if receipt:
            ambient_lane["routed_tasks"] += int(bool(receipt["routed"]))
            ambient_lane["incomplete_tasks"] += int(not bool(receipt["complete"]))
            for key in (
                "programs_enumerated", "demonstration_executions", "exact_programs",
                "probe_executions", "probe_rejections", "admitted_programs",
                "test_program_executions", "test_grid_executions", "runtime_failures",
                "behavior_classes",
            ):
                ambient_lane[key] += int(receipt[key])
        local = record["lanes"].get("local_transition", {})
        if local:
            local_lane["routed_tasks"] += int(bool(local.get("routed")))
            local_lane["incomplete_tasks"] += int(not bool(local.get("complete")))
            local_lane["behavior_classes"] += int(local.get("behavior_classes", 0))
            local_lane["stress_checks"] += int(local.get("stress_checks", 0))
        shape = record["lanes"].get("shape_constructors", {})
        receipt = shape.get("receipt", {})
        if receipt:
            shape_lane["routed_tasks"] += int(bool(receipt["routed"]))
            shape_lane["incomplete_tasks"] += int(not bool(receipt["complete"]))
            for key in (
                "programs_enumerated", "demonstration_executions",
                "execution_rejections", "exact_programs", "admitted_programs",
                "test_program_executions", "test_grid_executions",
                "runtime_failures", "behavior_classes",
            ):
                shape_lane[key] += int(receipt[key])
        axis = record["lanes"].get("axis_sequence", {})
        if axis:
            axis_lane["routed_tasks"] += int(bool(axis.get("routed")))
            axis_lane["incomplete_tasks"] += int(not bool(axis.get("complete")))
            axis_lane["behavior_classes"] += int(axis.get("behavior_classes", 0))
            axis_lane["programs"] += int(axis.get("programs", 0))
            axis_lane["stress_checks"] += int(axis.get("stress_checks", 0))
        composition = record["lanes"].get("object_composition", {})
        if composition:
            object_lane["routed_tasks"] += int(bool(composition.get("routed")))
            object_lane["incomplete_tasks"] += int(
                not bool(composition.get("complete"))
            )
            object_lane["behavior_classes"] += int(
                composition.get("behavior_classes", 0)
            )
            object_lane["programs"] += int(composition.get("programs", 0))
            object_lane["stress_checks"] += int(
                composition.get("stress_checks", 0)
            )
        periodic = record["lanes"].get("periodic_lattice", {})
        if periodic:
            periodic_lane["routed_tasks"] += int(bool(periodic.get("routed")))
            periodic_lane["incomplete_tasks"] += int(not bool(periodic.get("complete")))
            periodic_lane["behavior_classes"] += int(periodic.get("behavior_classes", 0))
            periodic_lane["programs"] += int(periodic.get("programs", 0))
            periodic_lane["demonstration_executions"] += int(
                periodic.get("demonstration_executions", 0)
            )
            periodic_lane["execution_rejections"] += int(
                periodic.get("execution_rejections", 0)
            )
    return {
        "totals": dict(sorted(totals.items())),
        "lanes": {
            "ambient_recovery": dict(sorted(ambient_lane.items())),
            "local_transition": dict(sorted(local_lane.items())),
            "shape_constructors": dict(sorted(shape_lane.items())),
            "axis_sequence": dict(sorted(axis_lane.items())),
            "object_composition": dict(sorted(object_lane.items())),
            "periodic_lattice": dict(sorted(periodic_lane.items())),
        },
    }


def freeze_corpus(
    root: str | Path,
    *,
    workers: int = 1,
    allow_provisional_ambient: bool = False,
    allow_provisional_shape: bool = False,
    allow_provisional_singletons: bool = False,
) -> dict[str, Any]:
    root = Path(root).resolve()
    challenges_path = root / "data" / "arc-agi_training_challenges.json"
    challenges = load_json(challenges_path)
    started = time.perf_counter()
    records = compile_falsification_corpus(
        challenges,
        workers=workers,
        allow_provisional_ambient=allow_provisional_ambient,
        allow_provisional_shape=allow_provisional_shape,
        allow_provisional_singletons=allow_provisional_singletons,
    )
    body: dict[str, Any] = {
        "schema": "komorebi.lasm_falsification.frozen_corpus",
        "schema_version": 2,
        "author": "Komorebi P.",
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "task_count": len(records),
        "task_ids_hash": sha256_record(tuple(records)),
        "grammar_contracts": {
            "ambient_recovery": AMBIENT_GRAMMAR_HASH,
            "axis_sequence": AXIS_SEQUENCE_GRAMMAR_HASH,
            "local_transition": LOCAL_TRANSITION_GRAMMAR_HASH,
            "object_composition": OBJECT_COMPOSITION_GRAMMAR_HASH,
            "periodic_lattice": PERIODIC_LATTICE_GRAMMAR_HASH,
            "shape_constructors": SHAPE_CONSTRUCTOR_GRAMMAR_HASH,
        },
        "promotion_policy": {
            "stable_ambient_schemas": "enabled",
            "provisional_ambient_schemas": (
                "explicitly enabled for the frozen retrospective challenger"
                if allow_provisional_ambient else "disabled"
            ),
            "stable_shape_schemas": "enabled",
            "provisional_shape_schemas": (
                "explicitly enabled for the frozen retrospective challenger"
                if allow_provisional_shape else "disabled"
            ),
            "provisional_single_source_lanes": (
                "explicitly enabled for the frozen retrospective challenger"
                if allow_provisional_singletons else "disabled"
            ),
            "runtime_default": "stable-only; provisional schemas require explicit opt-in",
        },
        "source_hashes": {"training_challenges": sha256_file(challenges_path)},
        "work": _work(records),
        "records": records,
        "runtime_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "Programs use labelled training demonstrations and sanitized test inputs. "
            "No public test solution is accepted or opened during this freeze."
        ),
    }
    semantic = {key: value for key, value in body.items() if key != "runtime_seconds"}
    body["semantic_hash"] = sha256_record(semantic)
    body["content_hash"] = sha256_record(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--include-provisional",
        action="store_true",
        help="Explicitly enable provisional ambient, shape, and singleton lanes",
    )
    args = parser.parse_args()
    result = freeze_corpus(
        args.root,
        workers=args.workers,
        allow_provisional_ambient=args.include_provisional,
        allow_provisional_shape=args.include_provisional,
        allow_provisional_singletons=args.include_provisional,
    )
    write_json(args.output, result)
    print({"content_hash": result["content_hash"], **result["work"]["totals"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["freeze_corpus", "main"]
