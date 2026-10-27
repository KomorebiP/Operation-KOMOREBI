"""Separate retrospective scorer for frozen PR-LASM Block 11 predictions.

The compiler/freeze module cannot accept labels.  This module opens public
training solutions only after the complete prediction ledger has a verified
content identity.  All reported scores are public-training engineering audits,
not ARC evaluation or hidden-test results.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.audit import score_submission
from komorebi_lasm_composition.model import canonical_value, sha256_record, validate_grid

from .action_schemas import ACTION_SCHEMAS_BY_NAME, PROVISIONAL
from .ambient_topology import PROVISIONAL_FAMILIES as PROVISIONAL_AMBIENT_FAMILIES
from .io import load_json, sha256_file, write_json
from .shape_layout import PROVISIONAL_SCHEMAS


CLAIM_BOUNDARY = (
    "Complete retrospective ARC-AGI public-training audit. Programs and test-input "
    "predictions froze before solutions opened. This is not public evaluation, "
    "private-test, hidden-test, ARC-AGI-3, or universal-generalization evidence."
)


def _explicitly_provisional_schema(key: str) -> bool:
    lane, _, schema_name = key.partition(":")
    return (
        lane == "residual_composition"
        or (
            lane == "action_schema"
            and schema_name in ACTION_SCHEMAS_BY_NAME
            and ACTION_SCHEMAS_BY_NAME[schema_name].status == PROVISIONAL
        )
        or (lane == "shape_layout" and schema_name in PROVISIONAL_SCHEMAS)
        or (
            lane == "ambient_topology"
            and schema_name in PROVISIONAL_AMBIENT_FAMILIES
        )
    )


def _outputs(value: Sequence[Any]) -> tuple[Any, ...]:
    return tuple(validate_grid(grid) for grid in value)


def _verify_freeze(frozen: Mapping[str, Any]) -> None:
    if frozen.get("phase") != "prediction_freeze_before_solution_open":
        raise ValueError("input is not a pre-score prediction freeze")
    if frozen.get("label_access") != "none":
        raise ValueError("freeze label boundary is invalid")
    claimed = frozen.get("content_hash")
    body = {
        key: value for key, value in frozen.items()
        if key not in {"content_hash", "runtime_seconds"}
    }
    if claimed != sha256_record(body):
        raise ValueError("freeze content hash mismatch")


def _candidate_for_lanes(
    record: Mapping[str, Any], allowed: frozenset[str],
) -> Mapping[str, Any] | None:
    behaviors = []
    for candidate in record.get("candidates", ()):
        mechanisms = [
            item for item in candidate.get("mechanisms", ())
            if item.get("lane") in allowed
        ]
        if mechanisms:
            behaviors.append({**candidate, "mechanisms": mechanisms})
    return behaviors[0] if len(behaviors) == 1 else None


def apply_overlay(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
    *,
    lanes: Iterable[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replace Attempt 2 with one frozen behavior; never inspect an answer."""

    allowed = frozenset(str(value) for value in lanes)
    submission = copy.deepcopy(baseline)
    ledger = {}
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
            item["reason"] = "compiler_error"
        elif record.get("candidates") and candidate is None:
            item["reason"] = "ambiguous_or_lane_excluded"
        elif candidate is not None:
            outputs = _outputs(candidate["test_predictions"])
            if task_id not in submission or len(outputs) != len(submission[task_id]):
                item["reason"] = "output_arity_mismatch"
            else:
                for index, output in enumerate(outputs):
                    submission[task_id][index]["attempt_2"] = [list(row) for row in output]
                item.update({
                    "committed": True,
                    "reason": "unique_exact_raster_behavior",
                    "behavior_hash": candidate["behavior_hash"],
                    "lanes": sorted({value["lane"] for value in candidate["mechanisms"]}),
                    "schema_keys": sorted({
                        f"{value['lane']}:{key}"
                        for value in candidate["mechanisms"]
                        for key in value.get("schema_keys", ())
                    }),
                })
        ledger[task_id] = item
    return canonical_value(submission), canonical_value(ledger)


def _baseline_exactness(
    baseline: Mapping[str, Any], solutions: Mapping[str, Any], task_id: str,
) -> tuple[bool, ...]:
    return tuple(
        validate_grid(item["attempt_1"]) == validate_grid(expected)
        or validate_grid(item["attempt_2"]) == validate_grid(expected)
        for item, expected in zip(baseline[task_id], solutions[task_id])
    )


def candidate_statistics(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    events = []
    activation_events = []
    schema_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for task_id in sorted(records):
        record = records[task_id]
        totals["route_eligible_tasks"] += int(bool(record.get("route_eligible")))
        totals["compiler_errors"] += int(bool(record.get("error")))
        candidates = tuple(record.get("candidates", ()))
        totals["tasks_with_candidates"] += int(bool(candidates))
        totals["ambiguous_tasks"] += int(len(candidates) > 1)
        if len(candidates) > 1:
            expected = _outputs(solutions[task_id])
            ambiguous_keys: set[str] = set()
            for candidate in candidates:
                predicted = _outputs(candidate["test_predictions"])
                behavior_exact = len(predicted) == len(expected) and predicted == expected
                totals[
                    "ambiguous_exact_behaviors" if behavior_exact
                    else "ambiguous_wrong_behaviors"
                ] += 1
                keys = {
                    f"{value['lane']}:{key}"
                    for value in candidate.get("mechanisms", ())
                    for key in value.get("schema_keys", ())
                }
                ambiguous_keys.update(keys)
                for key in keys:
                    schema_counts[key][
                        "ambiguous_exact_behaviors" if behavior_exact
                        else "ambiguous_wrong_behaviors"
                    ] += 1
            for key in ambiguous_keys:
                schema_counts[key]["ambiguous_task_activations"] += 1
            activation_events.append({
                "task_id": task_id,
                "status": "ambiguous",
                "exact": False,
                "new_exact_outputs": 0,
                "schema_keys": sorted(ambiguous_keys),
            })
            continue
        if len(candidates) != 1:
            continue
        totals["unique_behavior_tasks"] += 1
        candidate = candidates[0]
        predicted = _outputs(candidate["test_predictions"])
        expected = _outputs(solutions[task_id])
        arity_match = len(predicted) == len(expected)
        output_exactness = tuple(
            left == right for left, right in zip(predicted, expected)
        ) if arity_match else ()
        exact_outputs = sum(output_exactness)
        wrong_outputs = max(len(predicted), len(expected)) - exact_outputs
        task_exact = arity_match and all(output_exactness)
        baseline_exactness = _baseline_exactness(baseline, solutions, task_id)
        new_exact = sum(
            exact and not prior for exact, prior in zip(output_exactness, baseline_exactness)
        ) if arity_match else 0
        totals["exact_unique_tasks"] += int(task_exact)
        totals["wrong_unique_tasks"] += int(not task_exact)
        totals["exact_candidate_outputs"] += exact_outputs
        totals["wrong_candidate_outputs"] += wrong_outputs
        totals["new_exact_outputs"] += new_exact
        lanes = sorted({value["lane"] for value in candidate["mechanisms"]})
        schema_keys = sorted({
            f"{value['lane']}:{key}"
            for value in candidate["mechanisms"]
            for key in value.get("schema_keys", ())
        })
        for key in schema_keys:
            schema_counts[key]["activations"] += 1
            schema_counts[key]["exact"] += int(task_exact)
            schema_counts[key]["wrong"] += int(not task_exact)
            schema_counts[key]["new_exact_outputs"] += new_exact
        events.append({
            "task_id": task_id,
            "exact": task_exact,
            "output_exactness": list(output_exactness),
            "baseline_exactness": list(baseline_exactness),
            "new_exact_outputs": new_exact,
            "behavior_hash": candidate["behavior_hash"],
            "lanes": lanes,
            "schema_keys": schema_keys,
        })
        activation_events.append({
            "task_id": task_id,
            "status": "exact" if task_exact else "wrong",
            "exact": task_exact,
            "new_exact_outputs": new_exact,
            "schema_keys": schema_keys,
        })
    return {
        **{key: int(value) for key, value in sorted(totals.items())},
        "schema_statistics": {
            key: {name: int(value) for name, value in sorted(counts.items())}
            for key, counts in sorted(schema_counts.items())
        },
        "events": events,
        "activation_events": activation_events,
    }


def _prequential(
    statistics: Mapping[str, Any], *, minimum_support: int = 2,
    include_explicit_provisional: bool = False,
) -> dict[str, Any]:
    events = {item["task_id"]: item for item in statistics["activation_events"]}
    order = sorted(events, key=lambda task_id: hashlib.sha256(
        f"block11-transfer-prequential-v1:{task_id}".encode("ascii")
    ).hexdigest())
    evidence: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    transfer = []
    for position, task_id in enumerate(order):
        event = events[task_id]
        eligible = sorted(
            key for key in event["schema_keys"]
            if evidence[key]["exact"] >= minimum_support
            and not evidence[key]["wrong"]
            and not evidence[key]["ambiguous"]
            and (include_explicit_provisional or not _explicitly_provisional_schema(key))
        )
        if eligible and event["status"] != "ambiguous":
            totals["eligible_tasks"] += 1
            totals["exact"] += int(event["exact"])
            totals["wrong"] += int(not event["exact"])
            totals["new_exact_outputs"] += int(event["new_exact_outputs"] if event["exact"] else 0)
            transfer.append({
                "position": position,
                "task_id": task_id,
                "exact": bool(event["exact"]),
                "new_exact_outputs": int(event["new_exact_outputs"]),
                "eligible_schema_keys": eligible,
            })
        for key in event["schema_keys"]:
            evidence[key][event["status"]] += 1
    body = {
        "protocol": "predict-before-label over a fixed hash order",
        "minimum_earlier_exact_support": minimum_support,
        "include_explicit_provisional": include_explicit_provisional,
        **{key: int(value) for key, value in sorted(totals.items())},
        "events": transfer,
        "claim_boundary": "Public-training prequential evidence, not hidden evaluation.",
    }
    body["content_hash"] = sha256_record(body)
    return body


def _five_fold(
    statistics: Mapping[str, Any], *, minimum_support: int = 2,
    include_explicit_provisional: bool = False,
) -> dict[str, Any]:
    events = tuple(statistics["activation_events"])
    folds = {
        item["task_id"]: int.from_bytes(
            hashlib.sha256(f"block11-fivefold-v1:{item['task_id']}".encode("ascii")).digest()[:4],
            "big",
        ) % 5
        for item in events
    }
    totals: Counter[str] = Counter()
    fold_records = []
    for fold in range(5):
        evidence: dict[str, Counter[str]] = defaultdict(Counter)
        for event in events:
            if folds[event["task_id"]] == fold:
                continue
            for key in event["schema_keys"]:
                evidence[key][event["status"]] += 1
        selected = []
        for event in events:
            if folds[event["task_id"]] != fold:
                continue
            if event["status"] == "ambiguous":
                continue
            keys = sorted(
                key for key in event["schema_keys"]
                if evidence[key]["exact"] >= minimum_support
                and not evidence[key]["wrong"]
                and not evidence[key]["ambiguous"]
                and (include_explicit_provisional or not _explicitly_provisional_schema(key))
            )
            if not keys:
                continue
            totals["eligible_tasks"] += 1
            totals["exact"] += int(event["exact"])
            totals["wrong"] += int(not event["exact"])
            totals["new_exact_outputs"] += int(event["new_exact_outputs"] if event["exact"] else 0)
            selected.append({
                "task_id": event["task_id"],
                "exact": bool(event["exact"]),
                "new_exact_outputs": int(event["new_exact_outputs"]),
                "eligible_schema_keys": keys,
            })
        fold_records.append({"fold": fold, "events": selected})
    body = {
        "protocol": "five task-held-out folds over frozen public-training activations",
        "minimum_other_fold_support": minimum_support,
        "include_explicit_provisional": include_explicit_provisional,
        **{key: int(value) for key, value in sorted(totals.items())},
        "folds": fold_records,
        "claim_boundary": "Task-held-out public-training evidence, not hidden evaluation.",
    }
    body["content_hash"] = sha256_record(body)
    return body


def runtime_bank(statistics: Mapping[str, Any]) -> dict[str, Any]:
    entries = []
    for key, counts in sorted(statistics["schema_statistics"].items()):
        exact = int(counts.get("exact", 0))
        wrong = int(counts.get("wrong", 0))
        ambiguous_tasks = int(counts.get("ambiguous_task_activations", 0))
        wrong_enumerated = int(counts.get("ambiguous_wrong_behaviors", 0))
        explicitly_provisional = _explicitly_provisional_schema(key)
        if wrong:
            status = "rejected"
        elif explicitly_provisional:
            status = "provisional"
        elif exact >= 2:
            status = "stable"
        elif exact:
            status = "provisional"
        else:
            status = "unresolved"
        entries.append({
            "schema_key": key,
            "status": status,
            "exact_support": exact,
            "wrong_selectable_activations": wrong,
            "ambiguous_task_activations": ambiguous_tasks,
            "wrong_enumerated_behaviors_on_ambiguous_tasks": wrong_enumerated,
            "requires_exact_behavior_unanimity": True,
            "explicitly_provisional": explicitly_provisional,
        })
    body = {
        "schema": "komorebi.lasm_transfer.runtime_schema_bank",
        "schema_version": 1,
        "entries": entries,
        "contains_task_ids": False,
        "contains_predictions": False,
        "contains_expected_outputs": False,
        "contains_labels": False,
        "promotion_rule": (
            "Explicit provisional status is preserved; stable entries still require "
            "complete exact-behavior quotienting and abstain on disagreement."
        ),
        "authorization_role": "future frozen corpus; current score is a retrospective challenger overlay",
    }
    body["bank_id"] = sha256_record(body)
    return canonical_value(body)


def run_audit(
    frozen: Mapping[str, Any],
    baseline: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    _verify_freeze(frozen)
    records = frozen["records"]
    all_lanes = frozenset(
        mechanism["lane"]
        for record in records.values()
        for candidate in record.get("candidates", ())
        for mechanism in candidate.get("mechanisms", ())
    )
    submission, policy_ledger = apply_overlay(baseline, records, lanes=all_lanes)
    baseline_score = score_submission(baseline, solutions)
    score = score_submission(submission, solutions)
    statistics = candidate_statistics(records, solutions, baseline)
    prequential = _prequential(statistics)
    five_fold = _five_fold(statistics)
    challenger_prequential = _prequential(
        statistics, include_explicit_provisional=True,
    )
    challenger_five_fold = _five_fold(
        statistics, include_explicit_provisional=True,
    )

    exact_before = {
        (task_id, index)
        for task_id, expected_values in solutions.items()
        for index, expected in enumerate(expected_values)
        if (
            validate_grid(baseline[task_id][index]["attempt_1"]) == validate_grid(expected)
            or validate_grid(baseline[task_id][index]["attempt_2"]) == validate_grid(expected)
        )
    }
    exact_after = {
        (task_id, index)
        for task_id, expected_values in solutions.items()
        for index, expected in enumerate(expected_values)
        if (
            validate_grid(submission[task_id][index]["attempt_1"]) == validate_grid(expected)
            or validate_grid(submission[task_id][index]["attempt_2"]) == validate_grid(expected)
        )
    }
    lane_ablation = []
    lane_sets = [(lane,) for lane in sorted(all_lanes)]
    combined_lanes = tuple(sorted(all_lanes))
    if len(combined_lanes) > 1:
        lane_sets.append(combined_lanes)
    for lanes in lane_sets:
        value, _ = apply_overlay(baseline, records, lanes=lanes)
        lane_score = score_submission(value, solutions)
        lane_ablation.append({
            "lanes": list(lanes),
            "exact_outputs": int(lane_score["exact"]),
            "whole_tasks": int(lane_score["whole_tasks"]),
        })

    validation: dict[str, Any] = {
        "schema": "komorebi.lasm_transfer.public_training_audit",
        "schema_version": 1,
        "author": "Komorebi P.",
        "claim_boundary": CLAIM_BOUNDARY,
        "freeze_content_hash": frozen["content_hash"],
        "baseline": {
            "exact_outputs": int(baseline_score["exact"]),
            "whole_tasks": int(baseline_score["whole_tasks"]),
        },
        "block11": {
            "exact_outputs": int(score["exact"]),
            "whole_tasks": int(score["whole_tasks"]),
            "attempt_1_exact": int(score["attempt_1_exact"]),
            "attempt_2_incremental_exact": int(score["attempt_2_incremental_exact"]),
        },
        "net_exact_output_gain": int(score["exact"] - baseline_score["exact"]),
        "net_whole_task_gain": int(score["whole_tasks"] - baseline_score["whole_tasks"]),
        "lost_exact_outputs": [f"{task_id}:{index}" for task_id, index in sorted(exact_before - exact_after)],
        "new_exact_outputs": [f"{task_id}:{index}" for task_id, index in sorted(exact_after - exact_before)],
        "wrong_committed_candidates": int(statistics.get("wrong_candidate_outputs", 0)),
        "candidate_statistics": statistics,
        "prequential_transfer": prequential,
        "five_fold_transfer": five_fold,
        "challenger_prequential_transfer": challenger_prequential,
        "challenger_five_fold_transfer": challenger_five_fold,
        "lane_ablation": lane_ablation,
        "source_hashes": {
            "freeze_content": frozen["content_hash"],
            "baseline_content": sha256_record(baseline),
            "solutions_content": sha256_record(solutions),
            "submission_content": sha256_record(submission),
        },
    }
    validation["content_hash"] = sha256_record(validation)
    bank = runtime_bank(statistics)
    return submission, canonical_value(policy_ledger), canonical_value(validation), bank


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--solutions", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    args = parser.parse_args()
    frozen = load_json(args.freeze)
    baseline = load_json(args.baseline)
    solutions = load_json(args.solutions)
    submission, ledger, validation, bank = run_audit(frozen, baseline, solutions)
    write_json(args.submission, submission)
    write_json(args.ledger, ledger)
    write_json(args.validation, validation)
    write_json(args.bank, bank)
    print({
        "exact_outputs": validation["block11"]["exact_outputs"],
        "whole_tasks": validation["block11"]["whole_tasks"],
        "net_gain": validation["net_exact_output_gain"],
        "lost": len(validation["lost_exact_outputs"]),
        "wrong_commits": validation["wrong_committed_candidates"],
        "submission_sha256": sha256_file(args.submission),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CLAIM_BOUNDARY",
    "apply_overlay",
    "candidate_statistics",
    "run_audit",
    "runtime_bank",
]
