"""Public-training shadow audit for PR-LASM Block 10.

The compiler half of this module receives challenges, frozen Block 9 traces,
and labelled *training demonstrations*.  It never receives the public test
solutions.  Scoring is a separate, retrospective step performed only after
all candidate programs and their test-input behaviors have frozen.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import multiprocessing as mp
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.audit import score_submission
from komorebi_lasm_composition.model import (
    canonical_value,
    sha256_record,
    validate_grid,
)

from .diagnostics import (
    account_actual_work,
    load_frozen_block9_baseline,
)
from .experiment import (
    ActionArm,
    RepresentationArm,
    SearchArm,
    build_factorial_cell_record,
    build_factorial_validation_record,
    build_matched_factorial_plan,
)
from .targeted import compile_targeted_tools_traced
from .temporal import temporal_shadow_audit_record
from .tools import (
    ToolSynthesisLimits,
    synthesize_complete_scene_native_tools,
)


SCHEMA = "komorebi.lasm_action.public_training_shadow_audit"
SCHEMA_VERSION = 1
CLAIM_BOUNDARY = (
    "Complete retrospective ARC-AGI public-training shadow audit. Candidate "
    "generation sees labelled training demonstrations and sanitized test inputs, "
    "but no test solution. Public test solutions are opened only after programs "
    "and predictions freeze. No public evaluation, private-test, hidden-test, "
    "ARC-AGI-3, or universal-generalization result is claimed."
)


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            canonical_value(value),
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _outputs(value: Iterable[Any]) -> tuple[Any, ...]:
    return tuple(validate_grid(grid) for grid in value)


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


def _compile_worker(payload: tuple[str, Mapping[str, Any], Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    task_id, task, record = payload
    return task_id, compile_action_record(task_id, task, record)


def compile_corpus(
    challenges: Mapping[str, Any],
    block9_records: Mapping[str, Any],
    *,
    workers: int = 1,
) -> dict[str, Any]:
    """Compile the full corpus; neither this function nor workers receive labels."""

    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    if set(challenges) != set(block9_records):
        raise ValueError("challenge and frozen Block 9 record task sets differ")
    items = tuple(
        (str(task_id), challenges[task_id], block9_records[task_id])
        for task_id in sorted(challenges)
    )
    records: dict[str, Any] = {}
    if workers == 1:
        iterator = map(_compile_worker, items)
        pool = None
    else:
        context = mp.get_context("spawn" if os.name == "nt" else "fork")
        pool = context.Pool(processes=workers, maxtasksperchild=32)
        iterator = pool.imap_unordered(_compile_worker, items, chunksize=2)
    try:
        for task_id, record in iterator:
            records[task_id] = record
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    return {task_id: records[task_id] for task_id in sorted(records)}


def _candidate_for_lanes(
    record: Mapping[str, Any], lanes: frozenset[str],
) -> Mapping[str, Any] | None:
    behaviors = []
    for candidate in record.get("candidates", ()):
        mechanisms = [
            item for item in candidate.get("mechanisms", ())
            if item.get("lane") in lanes
        ]
        if mechanisms:
            behaviors.append({**candidate, "mechanisms": mechanisms})
    return behaviors[0] if len(behaviors) == 1 else None


def apply_overlay(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
    *,
    lanes: Iterable[str] = ("semantic", "targeted"),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Commit a unique behavior without consulting its held-out label."""

    allowed = frozenset(str(lane) for lane in lanes)
    submission = copy.deepcopy(baseline)
    ledger: dict[str, Any] = {}
    for task_id in sorted(records):
        record = records[task_id]
        candidate = _candidate_for_lanes(record, allowed)
        item: dict[str, Any] = {
            "route_eligible": bool(record.get("route_eligible")),
            "candidate_behaviors": len(record.get("candidates", ())),
            "committed": False,
            "reason": "no_candidate",
        }
        if record.get("error"):
            item["reason"] = "compile_error"
        elif record.get("candidates") and candidate is None:
            item["reason"] = "ambiguous_or_lane_excluded"
        elif candidate is not None:
            outputs = _outputs(candidate["test_predictions"])
            if task_id not in submission or len(outputs) != len(submission[task_id]):
                item["reason"] = "output_arity_mismatch"
            else:
                for index, grid in enumerate(outputs):
                    submission[task_id][index]["attempt_2"] = [list(row) for row in grid]
                item.update(
                    {
                        "committed": True,
                        "reason": "unique_exact_raster_behavior",
                        "behavior_hash": candidate["behavior_hash"],
                        "mechanism_keys": sorted(
                            {value["mechanism_key"] for value in candidate["mechanisms"]}
                        ),
                    }
                )
        ledger[task_id] = item
    return submission, ledger


def _candidate_statistics(
    records: Mapping[str, Any], solutions: Mapping[str, Any],
) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    by_mechanism: dict[str, Counter[str]] = defaultdict(Counter)
    events: list[dict[str, Any]] = []
    for task_id in sorted(records):
        record = records[task_id]
        totals["route_eligible_tasks"] += int(bool(record.get("route_eligible")))
        totals["compile_errors"] += int(bool(record.get("error")))
        candidates = tuple(record.get("candidates", ()))
        totals["tasks_with_candidates"] += int(bool(candidates))
        totals["ambiguous_tasks"] += int(len(candidates) > 1)
        if len(candidates) != 1:
            continue
        totals["unique_behavior_tasks"] += 1
        candidate = candidates[0]
        predicted = _outputs(candidate["test_predictions"])
        expected = _outputs(solutions[task_id])
        output_exactness = tuple(left == right for left, right in zip(predicted, expected))
        arity_match = len(predicted) == len(expected)
        task_exact = arity_match and all(output_exactness)
        exact_outputs = sum(output_exactness) if arity_match else 0
        wrong_outputs = max(len(predicted), len(expected)) - exact_outputs
        totals["exact_unique_tasks"] += int(task_exact)
        totals["wrong_unique_tasks"] += int(not task_exact)
        totals["exact_candidate_outputs"] += exact_outputs
        totals["wrong_candidate_outputs"] += wrong_outputs
        mechanism_keys = sorted(
            {value["mechanism_key"] for value in candidate["mechanisms"]}
        )
        lanes = sorted({value["lane"] for value in candidate["mechanisms"]})
        for key in mechanism_keys:
            by_mechanism[key]["activations"] += 1
            by_mechanism[key]["exact"] += int(task_exact)
            by_mechanism[key]["wrong"] += int(not task_exact)
        events.append(
            {
                "task_id": task_id,
                "exact": task_exact,
                "output_exactness": list(output_exactness),
                "behavior_hash": candidate["behavior_hash"],
                "mechanism_keys": mechanism_keys,
                "lanes": lanes,
            }
        )
    return {
        **{key: int(value) for key, value in sorted(totals.items())},
        "mechanism_statistics": {
            key: {name: int(value) for name, value in sorted(counts.items())}
            for key, counts in sorted(by_mechanism.items())
        },
        "events": events,
    }


def _runtime_action_bank(statistics: Mapping[str, Any]) -> dict[str, Any]:
    entries = []
    for key, counts in sorted(statistics["mechanism_statistics"].items()):
        activations = int(counts.get("activations", 0))
        exact = int(counts.get("exact", 0))
        wrong = int(counts.get("wrong", 0))
        if exact < 1 or wrong:
            continue
        entries.append(
            {
                "mechanism_key": key,
                "status": "stable" if activations >= 2 else "provisional",
                "support": activations,
                "incorrect_activations": wrong,
            }
        )
    body = {
        "schema": "komorebi.lasm_action.runtime_action_bank",
        "schema_version": SCHEMA_VERSION,
        "entries": entries,
        "contains_task_ids": False,
        "contains_expected_outputs": False,
        "authorization_role": "future frozen research artifact; not needed for current score",
    }
    body["bank_id"] = sha256_record(body)
    return body


def _prequential_transfer(statistics: Mapping[str, Any]) -> dict[str, Any]:
    events = {event["task_id"]: event for event in statistics["events"]}
    order = sorted(events, key=lambda task_id: hashlib.sha256(
        f"block10-action-prequential-v1:{task_id}".encode("ascii")
    ).hexdigest())
    evidence: dict[str, Counter[str]] = defaultdict(Counter)
    eligible = exact = wrong = 0
    transfer_events = []
    for position, task_id in enumerate(order):
        event = events[task_id]
        reusable = [
            key for key in event["mechanism_keys"]
            if evidence[key]["exact"] > 0 and evidence[key]["wrong"] == 0
        ]
        if reusable:
            eligible += 1
            exact += int(event["exact"])
            wrong += int(not event["exact"])
            transfer_events.append(
                {
                    "position": position,
                    "task_id": task_id,
                    "exact": bool(event["exact"]),
                    "eligible_mechanisms": sorted(reusable),
                }
            )
        for key in event["mechanism_keys"]:
            evidence[key]["exact" if event["exact"] else "wrong"] += 1
    result = {
        "protocol": "predict-before-label over hash-determined public-training order",
        "eligible_tasks": eligible,
        "exact": exact,
        "wrong": wrong,
        "events": transfer_events,
        "claim_boundary": "Public-training prequential evidence, not hidden evaluation.",
    }
    result["content_hash"] = sha256_record(result)
    return result


def _score_view(score: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "exact", "total", "rate", "whole_tasks", "task_total",
        "attempt_1_exact", "attempt_2_incremental_exact",
    )
    return {key: score[key] for key in keys}


def _retrospective_factorial(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> dict[str, Any]:
    cells = []
    for representation in RepresentationArm:
        for actions in ActionArm:
            for search in SearchArm:
                if actions is ActionArm.FROZEN:
                    submission = copy.deepcopy(baseline)
                    lanes: tuple[str, ...] = ()
                else:
                    lanes = ("targeted",) if search is SearchArm.CURRENT else (
                        "targeted", "semantic"
                    )
                    submission, _ = apply_overlay(baseline, records, lanes=lanes)
                score = score_submission(submission, solutions)
                cells.append(
                    {
                        "representation": representation.value,
                        "actions": actions.value,
                        "search": search.value,
                        "lanes": list(lanes),
                        **_score_view(score),
                    }
                )
    body = {
        "schema": "komorebi.lasm_action.retrospective_factorial",
        "schema_version": SCHEMA_VERSION,
        "cells": cells,
        "interpretation": (
            "Static ARC has no temporal continuation, so the new representation is a "
            "safety/contract factor and is not expected to improve this score directly."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    body["content_hash"] = sha256_record(body)
    return body


def _training_only_factorial(
    baseline: Any,
    records: Mapping[str, Any],
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    task_ids = tuple(sorted(records))
    plan = build_matched_factorial_plan(
        task_ids,
        cohort_partition_id=sha256_record(
            [task_id for task_id in task_ids if records[task_id]["route_eligible"]]
        ),
    )
    frozen_work = account_actual_work(baseline)
    frozen_totals = frozen_work.aggregate["totals"]
    semantic_work = {
        "proposals_considered": sum(
            int(record["semantic_trace"]["programs_considered"])
            for record in records.values()
        ),
        "executor_calls": sum(
            int(record["semantic_trace"]["executions_performed"])
            for record in records.values()
        ),
        "states_expanded": 0,
        "transitions_accepted": 0,
        "capsule_refinements": 0,
        "leakage_witnesses": 0,
    }
    targeted_exact = sum(
        int(record["targeted_trace"]["exact_programs"])
        for record in records.values()
    )
    semantic_exact = sum(
        int(record["semantic_trace"]["exact_programs"])
        for record in records.values()
    )
    targeted_proposals = sum(
        int(record["targeted_trace"]["programs_considered"])
        for record in records.values()
    )
    targeted_executions = sum(
        int(record["targeted_trace"]["demonstration_executions"])
        + int(record["targeted_trace"]["test_executions"])
        for record in records.values()
    )
    frozen_candidate_tasks = {
        task_id
        for task_id, item in frozen_work.per_task.items()
        if item.candidate_behaviors > 0
    }
    cells = []
    for condition in plan.conditions:
        expanded = condition.actions is ActionArm.EXPANDED
        widened = condition.search is SearchArm.WIDENED
        training_metrics = {
            "training_exact_programs": (
                int(frozen_totals["exact_programs"])
                + targeted_exact
                + (semantic_exact if widened else 0)
            ) if expanded else int(frozen_totals["exact_programs"]),
            "training_unique_behaviors": sum(
                bool(_candidate_for_lanes(
                    record,
                    frozenset(("targeted", "semantic") if widened else ("targeted",)),
                ))
                for record in records.values()
            ) + int(frozen_totals["behavior_classes"]) if expanded else int(frozen_totals["behavior_classes"]),
            "tasks_with_candidates": len(
                frozen_candidate_tasks
                | {
                    task_id
                    for task_id, record in records.items()
                    if _candidate_for_lanes(
                        record,
                        frozenset(("targeted", "semantic") if widened else ("targeted",)),
                    )
                }
            ) if expanded else int(frozen_work.aggregate["tasks_with_candidate_behaviors"]),
            "tasks_beyond_root": sum(
                item.states_expanded > 1 for item in frozen_work.per_task.values()
            ),
            "zero_transition_tasks": sum(
                item.transitions_accepted == 0 for item in frozen_work.per_task.values()
            ),
        }
        actual_work = {
            "proposals_considered": int(frozen_totals["proposals_considered"]),
            "states_expanded": int(frozen_totals["states_expanded"]),
            "transitions_accepted": int(frozen_totals["transitions_accepted"]),
            "executor_calls": 0,
            "capsule_refinements": 0,
            "leakage_witnesses": 0,
        }
        if expanded and widened:
            actual_work["proposals_considered"] += semantic_work["proposals_considered"]
            actual_work["executor_calls"] += semantic_work["executor_calls"]
        if expanded:
            actual_work["proposals_considered"] += targeted_proposals
            actual_work["executor_calls"] += targeted_executions
        cells.append(
            build_factorial_cell_record(
                plan,
                condition,
                replicate_salt=plan.replicate_salts[0],
                training_metrics=training_metrics,
                actual_work=actual_work,
                run_source_hashes=source_hashes,
            )
        )
    validation = build_factorial_validation_record(
        plan, cells, source_hashes=source_hashes,
    )
    return {"plan": plan.to_record(), "cells": cells, "validation": validation}


def run_audit(
    root: str | Path,
    *,
    workers: int = 1,
    records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    project = Path(root).resolve()
    challenges_path = project / "data/arc-agi_training_challenges.json"
    solutions_path = project / "data/arc-agi_training_solutions.json"
    baseline_path = project / "block9/results/block9_submission.json"
    block9_records_path = project / "block9/results/composition_records.json"
    challenges = load_json(challenges_path)
    baseline = load_json(baseline_path)
    block9_records = load_json(block9_records_path)
    frozen = load_frozen_block9_baseline(project)
    source_hashes = {
        "training_challenges": _source_hash(challenges_path),
        "block9_submission": _source_hash(baseline_path),
        "block9_records": _source_hash(block9_records_path),
    }
    source_root = project / "block10/src/komorebi_lasm_action"
    for path in sorted(source_root.glob("*.py")):
        source_hashes[f"block10_source/{path.name}"] = _source_hash(path)
    if records is None:
        records = compile_corpus(challenges, block9_records, workers=workers)
    records = {task_id: records[task_id] for task_id in sorted(records)}
    submission, policy = apply_overlay(baseline, records)

    # The retrospective label file is deliberately opened only after the
    # complete candidate ledger and both answer attempts have frozen.  This is
    # a process-level boundary in addition to the compiler's typed interfaces.
    solutions = load_json(solutions_path)
    source_hashes["training_solutions"] = _source_hash(solutions_path)
    baseline_score = score_submission(baseline, solutions)
    score = score_submission(submission, solutions)
    statistics = _candidate_statistics(records, solutions)
    exact_before = set(baseline_score["exact_keys"])
    exact_after = set(score["exact_keys"])
    new_exact = sorted(exact_after - exact_before)
    lost = sorted(exact_before - exact_after)
    attempt1_preserved = all(
        baseline[task_id][index]["attempt_1"]
        == submission[task_id][index]["attempt_1"]
        for task_id in baseline
        for index in range(len(baseline[task_id]))
    )
    compile_errors = {
        task_id: record["error"]
        for task_id, record in records.items()
        if record.get("error")
    }
    runtime_bank = _runtime_action_bank(statistics)
    validation: dict[str, Any] = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_hashes": source_hashes,
        "frozen_block9_baseline_id": frozen.baseline_id,
        "baseline": _score_view(baseline_score),
        "block10": _score_view(score),
        "net_exact_output_gain": int(score["exact"] - baseline_score["exact"]),
        "whole_task_gain": int(score["whole_tasks"] - baseline_score["whole_tasks"]),
        "new_exact_outputs": new_exact,
        "lost_exact_outputs": lost,
        "wrong_committed_outputs": int(statistics.get("wrong_candidate_outputs", 0)),
        "attempt_1_preserved": attempt1_preserved,
        "candidate_statistics": statistics,
        "compile_errors": compile_errors,
        "prequential_transfer": _prequential_transfer(statistics),
        "runtime_action_bank_id": runtime_bank["bank_id"],
        "release_gates": {
            "frozen_floor_332": baseline_score["exact"] == 332,
            "frozen_whole_tasks_301": baseline_score["whole_tasks"] == 301,
            "exact_outputs_at_least_347": score["exact"] >= 347,
            "whole_tasks_at_least_315": score["whole_tasks"] >= 315,
            "attempt1_preserved": attempt1_preserved,
            "no_lost_exact_outputs": not lost,
            "no_wrong_committed_outputs": int(statistics.get("wrong_candidate_outputs", 0)) == 0,
            "no_ambiguous_activations": int(statistics.get("ambiguous_tasks", 0)) == 0,
            "no_compile_errors": not compile_errors,
        },
    }
    validation["release_pass"] = all(validation["release_gates"].values())
    validation["content_hash"] = sha256_record(validation)
    return {
        "validation": validation,
        "records": records,
        "submission": submission,
        "policy_ledger": policy,
        "runtime_action_bank": runtime_bank,
        "training_factorial": _training_only_factorial(
            frozen,
            records,
            {
                key: value
                for key, value in source_hashes.items()
                if key != "training_solutions"
            },
        ),
        "retrospective_factorial": _retrospective_factorial(
            baseline, records, solutions,
        ),
        "temporal_shadow": temporal_shadow_audit_record(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    parser.add_argument("--records", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    records = load_json(args.records) if args.records else None
    bundle = run_audit(args.root, workers=args.workers, records=records)
    output = args.output_dir or (args.root / "block10/results")
    write_json(output / "action_records.json", bundle["records"])
    write_json(output / "block10_submission.json", bundle["submission"])
    write_json(output / "action_policy_ledger.json", bundle["policy_ledger"])
    write_json(output / "runtime_action_bank.json", bundle["runtime_action_bank"])
    write_json(output / "training_factorial.json", bundle["training_factorial"])
    write_json(output / "retrospective_factorial.json", bundle["retrospective_factorial"])
    write_json(output / "temporal_shadow_audit.json", bundle["temporal_shadow"])
    write_json(output / "block10_validation.json", bundle["validation"])
    validation = bundle["validation"]
    block10 = validation["block10"]
    print(
        "BLOCK10_AUDIT_PASS" if validation["release_pass"] else "BLOCK10_AUDIT_FAIL",
        f"exact={block10['exact']}/{block10['total']}",
        f"whole_tasks={block10['whole_tasks']}/{block10['task_total']}",
        f"gain={validation['net_exact_output_gain']}",
        f"wrong={validation['wrong_committed_outputs']}",
    )
    return 0 if validation["release_pass"] else 1


__all__ = [
    "CLAIM_BOUNDARY",
    "SCHEMA",
    "apply_overlay",
    "compile_action_record",
    "compile_corpus",
    "load_json",
    "main",
    "obstruction_route_eligible",
    "run_audit",
    "write_json",
]


if __name__ == "__main__":
    raise SystemExit(main())
