#!/usr/bin/env python3
"""Independently validate and score sealed ARC two-attempt predictions.

This program never imports or runs the solver. All exact-match metrics are
computed from the provided submission, challenges and separately stored labels.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"Expected a JSON object in {path.name}")
    return record


def validate_grid(grid: Any, location: str) -> None:
    if not isinstance(grid, list) or not 1 <= len(grid) <= 30:
        raise ValueError(f"{location}: grid height must be between 1 and 30")
    width = len(grid[0]) if isinstance(grid[0], list) else 0
    if not 1 <= width <= 30:
        raise ValueError(f"{location}: grid width must be between 1 and 30")
    for row in grid:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError(f"{location}: grid must be rectangular")
        if any(type(value) is not int or not 0 <= value <= 9 for value in row):
            raise ValueError(f"{location}: colors must be integers between 0 and 9")


def score(challenges: dict[str, Any], solutions: dict[str, Any], submission: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not challenges:
        raise ValueError("Cannot score an empty challenge set")
    if set(challenges) != set(solutions) or set(challenges) != set(submission):
        raise ValueError("Task identifier sets differ across challenges, solutions and submission")

    rows: list[dict[str, Any]] = []
    per_task: dict[str, Any] = {}
    for task_id in sorted(challenges):
        task = challenges[task_id]
        if not isinstance(task, dict) or not isinstance(task.get("test"), list) or not task["test"]:
            raise ValueError(f"{task_id}: missing or empty test set")
        truths = solutions[task_id]
        predictions = submission[task_id]
        if not isinstance(truths, list) or not isinstance(predictions, list):
            raise ValueError(f"{task_id}: solutions and predictions must be lists")
        if not len(task["test"]) == len(truths) == len(predictions):
            raise ValueError(f"{task_id}: challenge/solution/prediction output counts differ")

        task_pass1 = 0
        task_pass2 = 0
        for index, (test, truth, prediction) in enumerate(zip(task["test"], truths, predictions)):
            if not isinstance(test, dict) or "input" not in test:
                raise ValueError(f"{task_id}:{index}: missing test input")
            validate_grid(test["input"], f"{task_id}:{index}:input")
            validate_grid(truth, f"{task_id}:{index}:solution")
            if not isinstance(prediction, dict) or set(prediction) != {"attempt_1", "attempt_2"}:
                raise ValueError(f"{task_id}:{index}: prediction must contain exactly two attempts")
            for key in ("attempt_1", "attempt_2"):
                validate_grid(prediction[key], f"{task_id}:{index}:{key}")
            first = prediction["attempt_1"] == truth
            second = prediction["attempt_2"] == truth
            passed = first or second
            task_pass1 += int(first)
            task_pass2 += int(passed)
            rows.append({
                "task_id": task_id,
                "test_index": index,
                "attempt_1_exact": first,
                "attempt_2_exact": second,
                "attempt_2_incremental_exact": second and not first,
                "pass_at_2_exact": passed,
                "attempts_identical": prediction["attempt_1"] == prediction["attempt_2"],
                "expected_height": len(truth),
                "expected_width": len(truth[0]),
                "attempt_1_height": len(prediction["attempt_1"]),
                "attempt_1_width": len(prediction["attempt_1"][0]),
                "attempt_2_height": len(prediction["attempt_2"]),
                "attempt_2_width": len(prediction["attempt_2"][0]),
            })
        count = len(truths)
        per_task[task_id] = {
            "test_outputs": count,
            "pass_at_1_exact_outputs": task_pass1,
            "pass_at_2_exact_outputs": task_pass2,
            "pass_at_1_fraction": task_pass1 / count,
            "pass_at_2_fraction": task_pass2 / count,
            "whole_task_pass_at_1_exact": task_pass1 == count,
            "whole_task_pass_at_2_exact": task_pass2 == count,
        }

    output_count = len(rows)
    task_count = len(per_task)
    exact1 = sum(row["attempt_1_exact"] for row in rows)
    exact2 = sum(row["pass_at_2_exact"] for row in rows)
    metrics = {
        "tasks": task_count,
        "test_outputs": output_count,
        "submission_valid": True,
        "output_weighted_pass_at_1": {"exact": exact1, "total": output_count, "fraction": exact1 / output_count},
        "output_weighted_pass_at_2": {"exact": exact2, "total": output_count, "fraction": exact2 / output_count},
        "attempt_2_exact_outputs": sum(row["attempt_2_exact"] for row in rows),
        "attempt_2_incremental_exact_outputs": sum(row["attempt_2_incremental_exact"] for row in rows),
        "task_mean_pass_at_1_fraction": sum(row["pass_at_1_fraction"] for row in per_task.values()) / task_count,
        "task_mean_pass_at_2_fraction": sum(row["pass_at_2_fraction"] for row in per_task.values()) / task_count,
        "whole_task_pass_at_1": {"exact": sum(row["whole_task_pass_at_1_exact"] for row in per_task.values()), "total": task_count},
        "whole_task_pass_at_2": {"exact": sum(row["whole_task_pass_at_2_exact"] for row in per_task.values()), "total": task_count},
        "identical_attempt_outputs": sum(row["attempts_identical"] for row in rows),
        "metric_definitions": {
            "exact_match": "Two rectangular grids have identical shape and every cell value agrees.",
            "output_weighted_pass_at_2": "Mean exact success per test output, accepting either of the two attempts.",
            "task_mean_pass_at_2": "Average of each task's exact-output success fraction, giving every task equal weight.",
            "whole_task_pass_at_2": "Every test output in a task succeeds within two attempts.",
        },
        "per_task": per_task,
    }
    return metrics, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--solutions", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--label", required=True, help="Explicit provenance label, such as fresh frozen evaluation or historical reconstruction")
    parser.add_argument("--split", choices=("training", "evaluation", "other"), required=True)
    args = parser.parse_args()
    paths = {key: getattr(args, key).resolve() for key in ("challenges", "solutions", "submission")}
    # Hash the sealed predictions before opening the labels. No solver is imported.
    prediction_hash = sha256(paths["submission"])
    submission = read_object(paths["submission"])
    challenges = read_object(paths["challenges"])
    solutions = read_object(paths["solutions"])
    metrics, ledger = score(challenges, solutions, submission)
    if sha256(paths["submission"]) != prediction_hash:
        raise RuntimeError("Submission changed while scoring")
    record = {
        "schema": "komorebi.arc.independent-offline-score.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "dataset_split": args.split,
        "solver_calls_in_scorer": 0,
        "submission_hashed_before_labels_opened": True,
        "inputs": {key: {"path": str(path), "sha256": sha256(path)} for key, path in paths.items()},
        "scorer_source_sha256": sha256(Path(__file__).resolve()),
        **metrics,
    }
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    with args.ledger.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    record["per_test_ledger"] = {"path": str(args.ledger.resolve()), "sha256": sha256(args.ledger)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in record.items() if key not in {"per_task", "metric_definitions"}}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
