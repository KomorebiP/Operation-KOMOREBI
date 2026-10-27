"""Freeze the complete Block 11 corpus before public-training scoring.

This module has no solution-file parameter, imports no scorer, and reads only
challenges plus frozen Block 10 compilation records.  Attached test outputs
are sanitized by the constituent compilers.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from komorebi_lasm_composition.model import sha256_record

from .action_schemas import ACTION_SCHEMA_GRAMMAR_HASH
from .ambient_topology import GRAMMAR_HASH as AMBIENT_TOPOLOGY_GRAMMAR_HASH
from .compiler import compile_transfer_corpus
from .io import load_json, sha256_file, write_json
from .residual_composition import RESIDUAL_COMPOSITION_GRAMMAR_HASH
from .shape_layout import GRAMMAR_CONTRACT_HASH


def _work(records: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    lane_totals: dict[str, Counter[str]] = {
        "action_schema": Counter(),
        "shape_layout": Counter(),
        "residual_composition": Counter(),
        "ambient_topology": Counter(),
    }
    for record in records.values():
        totals["tasks"] += 1
        totals["route_eligible_tasks"] += int(bool(record["route_eligible"]))
        totals["compiler_errors"] += int(bool(record["error"]))
        totals["tasks_with_candidates"] += int(bool(record["candidates"]))
        totals["unique_behavior_tasks"] += int(len(record["candidates"]) == 1)
        totals["ambiguous_tasks"] += int(len(record["candidates"]) > 1)
        action = record["lanes"].get("action_schema", {})
        receipt = action.get("receipt")
        if receipt:
            lane_totals["action_schema"]["routed_tasks"] += 1
            for source, target in (
                ("programs_enumerated", "programs_enumerated"),
                ("demonstration_executions", "demonstration_executions"),
                ("training_exact_programs", "exact_programs"),
                ("admitted_exact_programs", "admitted_exact_programs"),
                ("test_executions", "test_executions"),
                ("behavior_classes", "behavior_classes"),
                ("execution_errors", "execution_errors"),
            ):
                lane_totals["action_schema"][target] += int(receipt[source])
        shape = record["lanes"].get("shape_layout", {})
        trace = shape.get("trace")
        if trace:
            lane_totals["shape_layout"]["routed_tasks"] += int(bool(trace["routed"]))
            for source, target in (
                ("programs_enumerated", "programs_enumerated"),
                ("demonstration_executions", "demonstration_executions"),
                ("exact_programs", "exact_programs"),
                ("test_executions", "test_executions"),
                ("behavior_classes", "behavior_classes"),
                ("execution_rejections", "execution_errors"),
            ):
                lane_totals["shape_layout"][target] += int(trace[source])
        residual = record["lanes"].get("residual_composition", {})
        receipt = residual.get("receipt")
        if receipt:
            lane_totals["residual_composition"]["routed_tasks"] += int(
                bool(receipt["route_eligible"])
            )
            lane_totals["residual_composition"]["incomplete_tasks"] += int(
                not bool(receipt["enumeration_complete"])
            )
            for source, target in (
                ("atomic_syntax_generated", "atomic_syntax_generated"),
                ("shape_syntax_generated", "shape_syntax_generated"),
                ("states_expanded", "states_expanded"),
                ("proposals_executed", "proposals_executed"),
                ("executor_calls", "executor_calls"),
                ("execution_errors", "execution_errors"),
                ("transitions_accepted", "transitions_accepted"),
                ("packet_recomputations", "packet_recomputations"),
                ("exact_programs", "exact_programs"),
                ("behavior_classes", "behavior_classes"),
            ):
                lane_totals["residual_composition"][target] += int(receipt[source])
        ambient = record["lanes"].get("ambient_topology", {})
        receipt = ambient.get("receipt")
        if receipt:
            lane_totals["ambient_topology"]["routed_tasks"] += int(
                bool(receipt["routed"])
            )
            lane_totals["ambient_topology"]["incomplete_tasks"] += int(
                not bool(receipt["complete"])
            )
            for source, target in (
                ("programs_enumerated", "programs_enumerated"),
                ("demonstration_executions", "demonstration_executions"),
                ("inapplicable_executions", "inapplicable_executions"),
                ("mismatch_executions", "mismatch_executions"),
                ("exact_programs", "exact_programs"),
                ("admitted_programs", "admitted_programs"),
                ("test_program_executions", "test_program_executions"),
                ("test_grid_executions", "test_grid_executions"),
                ("runtime_failures", "runtime_failures"),
                ("behavior_classes", "behavior_classes"),
            ):
                lane_totals["ambient_topology"][target] += int(receipt[source])
    return {
        "totals": {key: int(value) for key, value in sorted(totals.items())},
        "lanes": {
            lane: {key: int(value) for key, value in sorted(values.items())}
            for lane, values in lane_totals.items()
        },
    }


def freeze_corpus(root: str | Path, *, workers: int = 1) -> dict[str, Any]:
    root = Path(root).resolve()
    challenges_path = root / "data/arc-agi_training_challenges.json"
    records_path = root / "block10/results/action_records.json"
    challenges = load_json(challenges_path)
    block10_records = load_json(records_path)
    records = compile_transfer_corpus(
        challenges,
        block10_records,
        workers=workers,
        allow_provisional_action=True,
        allow_provisional_shape=True,
        allow_provisional_residual=True,
        allow_provisional_ambient=True,
    )
    body: dict[str, Any] = {
        "schema": "komorebi.lasm_transfer.frozen_corpus",
        "schema_version": 1,
        "author": "Komorebi P.",
        "phase": "prediction_freeze_before_solution_open",
        "label_access": "none",
        "task_count": len(records),
        "task_ids_hash": sha256_record(tuple(records)),
        "grammar_contracts": {
            "action_schema": ACTION_SCHEMA_GRAMMAR_HASH,
            "shape_layout": GRAMMAR_CONTRACT_HASH,
            "residual_composition": RESIDUAL_COMPOSITION_GRAMMAR_HASH,
            "ambient_topology": AMBIENT_TOPOLOGY_GRAMMAR_HASH,
        },
        "promotion_policy": {
            "stable_schemas": "enabled",
            "provisional_action_box_render": "explicitly enabled for retrospective challenger overlay",
            "provisional_periodic_extract": "explicitly enabled for retrospective challenger overlay",
            "provisional_residual_words": "explicitly enabled for retrospective challenger overlay",
            "provisional_ambient_families": "explicitly enabled for retrospective challenger overlay",
            "runtime_default": "provisional schemas disabled unless explicitly requested",
        },
        "source_hashes": {
            "training_challenges": sha256_file(challenges_path),
            "block10_action_records": sha256_file(records_path),
        },
        "work": _work(records),
        "records": records,
        "claim_boundary": (
            "Programs use labelled training demonstrations and sanitized test inputs. "
            "No public test solution is accepted or opened during this freeze."
        ),
    }
    body["content_hash"] = sha256_record(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    result = freeze_corpus(args.root, workers=args.workers)
    write_json(args.output, result)
    print({
        "content_hash": result["content_hash"],
        **result["work"]["totals"],
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["freeze_corpus", "main"]
