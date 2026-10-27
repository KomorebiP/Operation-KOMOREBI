"""Retrospective public-training audit for frozen PR-LASM Block 12 output.

The separate freeze is verified before this module opens public-training
solutions.  Reported measurements are engineering audits, never official ARC
evaluation or hidden-test claims.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

from komorebi_lasm_compiler.audit import score_submission
from komorebi_lasm_composition.model import canonical_value, sha256_record, validate_grid

from .io import load_json, sha256_file, write_json


CLAIM_BOUNDARY = (
    "Complete retrospective ARC-AGI public-training audit. Programs and "
    "test-input predictions froze before solutions opened. This is not public "
    "evaluation, private-test, hidden-test, ARC-AGI-3, or universal transfer evidence."
)


def _verify_freeze(frozen: Mapping[str, Any]) -> None:
    if frozen.get("phase") != "prediction_freeze_before_solution_open":
        raise ValueError("input is not a pre-score prediction freeze")
    if frozen.get("label_access") != "none":
        raise ValueError("freeze label boundary is invalid")
    claimed = frozen.get("content_hash")
    body = {key: value for key, value in frozen.items() if key != "content_hash"}
    if claimed != sha256_record(body):
        raise ValueError("freeze content hash mismatch")


def _outputs(value: Sequence[Any]) -> tuple[Any, ...]:
    return tuple(validate_grid(grid) for grid in value)


def apply_overlay(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Replace only Attempt 2 when one complete raster behavior survives."""

    submission = copy.deepcopy(baseline)
    ledger: dict[str, Any] = {}
    for task_id in sorted(records):
        record = records[task_id]
        candidates = tuple(record.get("candidates", ()))
        item: dict[str, Any] = {
            "candidate_behaviors": len(candidates),
            "committed": False,
            "reason": "no_candidate",
        }
        if record.get("error"):
            item["reason"] = "compiler_error"
        elif not record.get("selection_complete", False):
            item["reason"] = "incomplete_search_abstention"
        elif len(candidates) > 1:
            item["reason"] = "ambiguous_abstention"
        elif len(candidates) == 1:
            outputs = _outputs(candidates[0]["test_predictions"])
            if task_id not in submission or len(outputs) != len(submission[task_id]):
                item["reason"] = "output_arity_mismatch"
            else:
                for index, output in enumerate(outputs):
                    submission[task_id][index]["attempt_2"] = [list(row) for row in output]
                item.update({
                    "committed": True,
                    "reason": "unique_exact_raster_behavior",
                    "behavior_hash": candidates[0]["behavior_hash"],
                    "lanes": sorted({
                        mechanism["lane"]
                        for mechanism in candidates[0]["mechanisms"]
                    }),
                    "schema_keys": sorted({
                        f"{mechanism['lane']}:{schema}"
                        for mechanism in candidates[0]["mechanisms"]
                        for schema in mechanism.get("schema_keys", ())
                    }),
                })
        ledger[task_id] = item
    return canonical_value(submission), canonical_value(ledger)


def _exactness(
    submission: Mapping[str, Any],
    solutions: Mapping[str, Any],
    task_id: str,
) -> tuple[bool, ...]:
    return tuple(
        validate_grid(item["attempt_1"]) == validate_grid(expected)
        or validate_grid(item["attempt_2"]) == validate_grid(expected)
        for item, expected in zip(submission[task_id], solutions[task_id])
    )


def candidate_statistics(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    totals: Counter[str] = Counter()
    schemas: dict[str, Counter[str]] = defaultdict(Counter)
    events = []
    for task_id, record in sorted(records.items()):
        candidates = tuple(record.get("candidates", ()))
        totals["tasks_with_candidates"] += int(bool(candidates))
        totals["ambiguous_tasks"] += int(len(candidates) > 1)
        if not record.get("selection_complete", False):
            totals["incomplete_candidate_tasks"] += int(bool(candidates))
            continue
        if len(candidates) != 1:
            continue
        candidate = candidates[0]
        predicted = _outputs(candidate["test_predictions"])
        expected = _outputs(solutions[task_id])
        arity_match = len(predicted) == len(expected)
        exactness = tuple(a == b for a, b in zip(predicted, expected)) if arity_match else ()
        exact_outputs = sum(exactness)
        wrong_outputs = max(len(predicted), len(expected)) - exact_outputs
        task_exact = arity_match and all(exactness)
        prior = _exactness(baseline, solutions, task_id)
        new = sum(now and not before for now, before in zip(exactness, prior)) if arity_match else 0
        totals["unique_behavior_tasks"] += 1
        totals["exact_unique_tasks"] += int(task_exact)
        totals["wrong_unique_tasks"] += int(not task_exact)
        totals["exact_candidate_outputs"] += exact_outputs
        totals["wrong_candidate_outputs"] += wrong_outputs
        totals["new_exact_outputs"] += new
        keys = sorted({
            f"{mechanism['lane']}:{schema}"
            for mechanism in candidate["mechanisms"]
            for schema in mechanism.get("schema_keys", ())
        })
        for key in keys:
            schemas[key]["activations"] += 1
            schemas[key]["exact"] += int(task_exact)
            schemas[key]["wrong"] += int(not task_exact)
            schemas[key]["new_exact_outputs"] += new
        events.append({
            "task_id": task_id,
            "exact": task_exact,
            "output_exactness": list(exactness),
            "baseline_exactness": list(prior),
            "new_exact_outputs": new,
            "behavior_hash": candidate["behavior_hash"],
            "schema_keys": keys,
        })
    return {
        **dict(sorted(totals.items())),
        "schema_statistics": {
            key: dict(sorted(value.items())) for key, value in sorted(schemas.items())
        },
        "events": events,
    }


def prequential_transfer(
    statistics: Mapping[str, Any],
    *,
    minimum_support: int = 2,
) -> dict[str, Any]:
    """Reveal each frozen candidate label only after checking the prior bank."""

    events = list(statistics["events"])
    events.sort(key=lambda item: hashlib.sha256(
        f"block12-prequential-v1:{item['task_id']}".encode("ascii")
    ).hexdigest())
    evidence: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    transfers = []
    for position, event in enumerate(events):
        eligible = sorted(
            key for key in event["schema_keys"]
            if evidence[key]["exact"] >= minimum_support
            and evidence[key]["wrong"] == 0
        )
        if eligible:
            totals["eligible"] += 1
            totals["exact"] += int(event["exact"])
            totals["wrong"] += int(not event["exact"])
            totals["new_exact_outputs"] += int(event["new_exact_outputs"])
            transfers.append({
                "position": position,
                "task_id": event["task_id"],
                "exact": event["exact"],
                "eligible_schema_keys": eligible,
            })
        for key in event["schema_keys"]:
            evidence[key]["exact" if event["exact"] else "wrong"] += 1
    return {
        "minimum_prior_exact_support": minimum_support,
        "interpretation": (
            "public-corpus schema-support eligibility simulation over already "
            "compiled per-task candidates; not end-to-end held-out discovery"
        ),
        **dict(sorted(totals.items())),
        "events": transfers,
    }


def five_fold_transfer(
    statistics: Mapping[str, Any],
    *,
    minimum_support: int = 2,
) -> dict[str, Any]:
    """Promote schemas on four deterministic folds before scoring the fifth."""

    events = list(statistics["events"])
    folds = {
        event["task_id"]: int(hashlib.sha256(
            f"block12-fivefold-v1:{event['task_id']}".encode("ascii")
        ).hexdigest(), 16) % 5
        for event in events
    }
    totals: Counter[str] = Counter()
    rows = []
    for fold in range(5):
        evidence: dict[str, Counter[str]] = defaultdict(Counter)
        for event in events:
            if folds[event["task_id"]] == fold:
                continue
            for key in event["schema_keys"]:
                evidence[key]["exact" if event["exact"] else "wrong"] += 1
        eligible_schemas = {
            key for key, counts in evidence.items()
            if counts["exact"] >= minimum_support and counts["wrong"] == 0
        }
        for event in events:
            if folds[event["task_id"]] != fold:
                continue
            matched = sorted(set(event["schema_keys"]) & eligible_schemas)
            if not matched:
                continue
            totals["eligible"] += 1
            totals["exact"] += int(event["exact"])
            totals["wrong"] += int(not event["exact"])
            totals["new_exact_outputs"] += int(event["new_exact_outputs"])
            rows.append({
                "fold": fold,
                "task_id": event["task_id"],
                "exact": event["exact"],
                "eligible_schema_keys": matched,
            })
    return {
        "folds": 5,
        "minimum_training_exact_support": minimum_support,
        "interpretation": (
            "public-corpus schema-support eligibility simulation over already "
            "compiled per-task candidates; not end-to-end held-out discovery"
        ),
        **dict(sorted(totals.items())),
        "events": rows,
    }


def audit_corpus(
    root: str | Path,
    frozen_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = Path(root).resolve()
    frozen_path = Path(frozen_path).resolve()
    baseline_path = root / "block11" / "results" / "block11_submission.json"
    solutions_path = root / "data" / "arc-agi_training_solutions.json"
    frozen = load_json(frozen_path)
    _verify_freeze(frozen)
    baseline = load_json(baseline_path)
    solutions = load_json(solutions_path)
    submission, ledger = apply_overlay(baseline, frozen["records"])
    baseline_score = score_submission(baseline, solutions)
    block12_score = score_submission(submission, solutions)
    stats = candidate_statistics(frozen["records"], solutions, baseline)
    new_exact = sorted(set(block12_score["exact_keys"]) - set(baseline_score["exact_keys"]))
    lost_exact = sorted(set(baseline_score["exact_keys"]) - set(block12_score["exact_keys"]))
    wrong_commits = sum(
        not event["exact"] for event in stats["events"]
        if ledger[event["task_id"]]["committed"]
    )
    report: dict[str, Any] = {
        "schema": "komorebi.lasm_falsification.public_training_audit",
        "schema_version": 2,
        "author": "Komorebi P.",
        "freeze_content_hash": frozen["content_hash"],
        "source_hashes": {
            "freeze": sha256_file(frozen_path),
            "baseline": sha256_file(baseline_path),
            "solutions": sha256_file(solutions_path),
        },
        "baseline": {
            "exact_outputs": baseline_score["exact"],
            "whole_tasks": baseline_score["whole_tasks"],
        },
        "block12": {
            "exact_outputs": block12_score["exact"],
            "whole_tasks": block12_score["whole_tasks"],
            "attempt_1_exact": block12_score["attempt_1_exact"],
            "attempt_2_incremental_exact": block12_score["attempt_2_incremental_exact"],
        },
        "net_exact_output_gain": block12_score["exact"] - baseline_score["exact"],
        "net_whole_task_gain": block12_score["whole_tasks"] - baseline_score["whole_tasks"],
        "new_exact_outputs": new_exact,
        "lost_exact_outputs": lost_exact,
        "wrong_committed_candidates": wrong_commits,
        "candidate_statistics": stats,
        "prequential_transfer": prequential_transfer(stats),
        "five_fold_transfer": five_fold_transfer(stats),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    report["content_hash"] = sha256_record(report)
    return report, submission, ledger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    report, submission, ledger = audit_corpus(args.root, args.frozen)
    write_json(args.validation, report)
    write_json(args.submission, submission)
    write_json(args.ledger, ledger)
    print({
        "exact_outputs": report["block12"]["exact_outputs"],
        "whole_tasks": report["block12"]["whole_tasks"],
        "net_gain": report["net_exact_output_gain"],
        "lost": len(report["lost_exact_outputs"]),
        "wrong_commits": report["wrong_committed_candidates"],
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CLAIM_BOUNDARY", "apply_overlay", "audit_corpus", "candidate_statistics",
    "five_fold_transfer", "main", "prequential_transfer",
]
