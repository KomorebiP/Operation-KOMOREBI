#!/usr/bin/env python3
from __future__ import annotations

"""Fit the static ARC PR-LASM Bayesian program posterior on public training data.

The script never reads the ARC public-evaluation or test split.  It partitions
public training task IDs deterministically into a calibration subset and a
locked training holdout, learns hierarchical Beta priors and a Bayesian ridge
reliability model, then reports both calibration and holdout selection scores.
"""

import argparse
from dataclasses import dataclass
from hashlib import blake2b
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_arc2 import entry
from komorebi_arc2.atlas import ARCAtlasAnalyzer, analyze_task_signal
from komorebi_arc2.lasm_bayesian import (
    BayesianProjectorResolvedLargeSignalModel,
    BetaPrior,
    CalibrationAccumulator,
    LASMCalibration,
    candidate_metrics,
)


@dataclass
class RawRecord:
    candidate: entry.RuleCandidate
    metrics: Any
    task_state: Any
    success_fraction: float


def split_is_holdout(task_id: str, holdout_fraction: float) -> bool:
    digest = blake2b(task_id.encode("ascii"), digest_size=8, person=b"ARC2-LASM-split").digest()
    value = int.from_bytes(digest, "big") / float(2**64)
    return value < holdout_fraction


def candidate_success(candidate: entry.RuleCandidate, answers: list[list[list[int]]]) -> float:
    if not answers:
        return 0.0
    hits = 0
    for index, answer in enumerate(answers):
        if index < len(candidate.grids) and entry.exact(candidate.grids[index], entry.as_array(answer)):
            hits += 1
    return hits / len(answers)


def select_calibration_candidates(candidates: list[entry.RuleCandidate], maximum: int) -> list[entry.RuleCandidate]:
    """Select a family-diverse calibration design.

    Calibration must observe reusable structural families even when a task has
    many exact local residual refinements.  The design therefore takes one
    representative per family before adding a second round and then the best
    approximate frontier.
    """
    exact_candidates = sorted(
        (candidate for candidate in candidates if candidate.train_error == 0),
        key=entry._candidate_family_priority,
    )
    approximate = sorted(
        (candidate for candidate in candidates if candidate.train_error != 0),
        key=lambda candidate: (candidate.train_error, *entry._candidate_family_priority(candidate)),
    )
    selected: list[entry.RuleCandidate] = []
    seen: set[tuple[str, ...]] = set()
    residual_counts: dict[str, int] = {}

    def add(candidate: entry.RuleCandidate) -> bool:
        signature = tuple(entry.canonical(grid) for grid in candidate.grids)
        if signature in seen:
            return False
        if candidate.family.startswith("residual_"):
            count = residual_counts.get(candidate.family, 0)
            if count >= 2:
                return False
            residual_counts[candidate.family] = count + 1
        seen.add(signature)
        selected.append(candidate)
        return True

    exact_by_family: dict[str, list[entry.RuleCandidate]] = {}
    for candidate in exact_candidates:
        exact_by_family.setdefault(candidate.family, []).append(candidate)
    ordered_families = sorted(
        exact_by_family,
        key=lambda family: entry._candidate_family_priority(exact_by_family[family][0]),
    )
    for family in ordered_families:
        add(exact_by_family[family][0])
        if len(selected) >= maximum:
            return selected
    depth = 1
    while len(selected) < maximum:
        available = False
        for family in ordered_families:
            values = exact_by_family[family]
            if depth < len(values):
                available = True
                add(values[depth])
                if len(selected) >= maximum:
                    return selected
        if not available:
            break
        depth += 1

    family_seen: set[str] = set()
    for candidate in approximate:
        if candidate.family in family_seen:
            continue
        family_seen.add(candidate.family)
        add(candidate)
        if len(selected) >= maximum:
            return selected
    for candidate in approximate:
        add(candidate)
        if len(selected) >= maximum:
            break
    return selected


def preliminary_calibration(records: list[RawRecord], families: list[str], prior_strength: float) -> LASMCalibration:
    family_values: dict[str, list[float]] = {family: [] for family in families}
    route_values: dict[str, dict[str, list[float]]] = {}
    for record in records:
        family_values.setdefault(record.candidate.family, []).append(record.success_fraction)
        route_values.setdefault(record.task_state.primary_route, {}).setdefault(record.candidate.family, []).append(record.success_fraction)
    family_priors: dict[str, BetaPrior] = {}
    for family in families:
        values = family_values.get(family, [])
        family_priors[family] = BetaPrior(
            1.0 + prior_strength * sum(values),
            1.0 + prior_strength * (len(values) - sum(values)),
        )
    family_priors["__unknown__"] = BetaPrior(1.0, 4.0)
    route_priors: dict[str, dict[str, BetaPrior]] = {}
    from komorebi_arc2.atlas import ROUTE_NAMES
    for route in ROUTE_NAMES:
        route_priors[route] = {"__unknown__": BetaPrior(1.0, 4.0)}
        for family in families:
            values = route_values.get(route, {}).get(family, [])
            if values:
                route_priors[route][family] = BetaPrior(
                    1.0 + prior_strength * sum(values),
                    1.0 + prior_strength * (len(values) - sum(values)),
                )
    return LASMCalibration(
        model_version="preliminary",
        families=tuple(families),
        family_priors=family_priors,
        route_family_priors=route_priors,
        regression=None,
        training_metadata={},
    )


def collect_records(
    tasks: dict[str, dict],
    solutions: dict[str, list[list[list[int]]]],
    task_ids: list[str],
    time_limit: float,
    maximum_candidates: int,
    analyzer: ARCAtlasAnalyzer,
) -> tuple[list[RawRecord], dict[str, Any]]:
    records: list[RawRecord] = []
    family_counts: dict[str, int] = {}
    started = time.perf_counter()
    exact_fit_candidates = 0
    for number, task_id in enumerate(task_ids, 1):
        task = tasks[task_id]
        train = [(entry.as_array(pair["input"]), entry.as_array(pair["output"])) for pair in task.get("train", [])]
        tests = [entry.as_array(pair["input"]) for pair in task.get("test", [])]
        candidates = entry.deduplicate_candidates(entry.collect_candidates(train, tests, time_limit=time_limit))
        selected = select_calibration_candidates(candidates, maximum_candidates)
        task_state = analyze_task_signal(train, analyzer)
        for candidate in selected:
            metrics = candidate_metrics(candidate, train, analyzer)
            success = candidate_success(candidate, solutions.get(task_id, []))
            records.append(RawRecord(candidate, metrics, task_state, success))
            family_counts[candidate.family] = family_counts.get(candidate.family, 0) + 1
            exact_fit_candidates += int(candidate.train_error == 0)
        if number <= 3 or number % 50 == 0 or number == len(task_ids):
            print(
                f"[{number:4d}/{len(task_ids):4d}] {task_id} candidates={len(candidates):3d} "
                f"selected={len(selected):2d} records={len(records):5d} elapsed={time.perf_counter()-started:.1f}s",
                flush=True,
            )
    return records, {
        "tasks": len(task_ids),
        "records": len(records),
        "exact_fit_candidate_records": exact_fit_candidates,
        "family_counts": family_counts,
        "elapsed_seconds": time.perf_counter() - started,
    }


def evaluate_model(
    model: BayesianProjectorResolvedLargeSignalModel,
    tasks: dict[str, dict],
    solutions: dict[str, list[list[list[int]]]],
    task_ids: list[str],
    time_limit: float,
) -> dict[str, Any]:
    total = 0
    correct = 0
    attempt_1 = 0
    attempt_2 = 0
    whole_tasks = 0
    entropy: list[float] = []
    disagreement: list[float] = []
    started = time.perf_counter()
    for number, task_id in enumerate(task_ids, 1):
        task = tasks[task_id]
        diagnostics: dict[str, object] = {}
        prediction = entry.solve_task(task, time_limit=time_limit, lasm_model=model, diagnostics=diagnostics)
        answers = solutions.get(task_id, [])
        task_hits = 0
        for index, answer in enumerate(answers):
            total += 1
            target = entry.as_array(answer)
            first = index < len(prediction) and entry.exact(entry.as_array(prediction[index]["attempt_1"]), target)
            second = index < len(prediction) and entry.exact(entry.as_array(prediction[index]["attempt_2"]), target)
            attempt_1 += int(first)
            attempt_2 += int(second)
            correct += int(first or second)
            task_hits += int(first or second)
        whole_tasks += int(task_hits == len(answers) and bool(answers))
        if "posterior_entropy" in diagnostics:
            entropy.append(float(diagnostics["posterior_entropy"]))
        if "model_disagreement" in diagnostics:
            disagreement.append(float(diagnostics["model_disagreement"]))
        if number <= 3 or number % 50 == 0 or number == len(task_ids):
            print(
                f"eval [{number:4d}/{len(task_ids):4d}] {task_id} cumulative={correct}/{total} "
                f"elapsed={time.perf_counter()-started:.1f}s",
                flush=True,
            )
    return {
        "tasks": len(task_ids),
        "whole_tasks_correct": whole_tasks,
        "outputs_correct": correct,
        "outputs_total": total,
        "score": correct / max(1, total),
        "attempt_1_correct": attempt_1,
        "attempt_2_correct": attempt_2,
        "mean_posterior_entropy": float(np.mean(entropy)) if entropy else None,
        "mean_model_disagreement": float(np.mean(disagreement)) if disagreement else None,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the Bayesian PR-LASM ARC2 program posterior")
    parser.add_argument("--challenges", required=True)
    parser.add_argument("--solutions", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--holdout-fraction", type=float, default=0.20)
    parser.add_argument("--time-limit", type=float, default=0.08)
    parser.add_argument("--maximum-candidates", type=int, default=16)
    parser.add_argument("--prior-strength", type=float, default=2.0)
    parser.add_argument("--max-calibration-tasks", type=int, default=None)
    parser.add_argument("--max-holdout-tasks", type=int, default=None)
    args = parser.parse_args()

    tasks = entry.load_tasks_from_path(args.challenges)
    solutions = entry.load_solutions_from_path(args.solutions)
    calibration_ids = [task_id for task_id in tasks if not split_is_holdout(task_id, args.holdout_fraction)]
    holdout_ids = [task_id for task_id in tasks if split_is_holdout(task_id, args.holdout_fraction)]
    if args.max_calibration_tasks is not None:
        calibration_ids = calibration_ids[: args.max_calibration_tasks]
    if args.max_holdout_tasks is not None:
        holdout_ids = holdout_ids[: args.max_holdout_tasks]
    print(f"calibration_tasks={len(calibration_ids)} holdout_tasks={len(holdout_ids)}")

    analyzer = ARCAtlasAnalyzer()
    records, collection_report = collect_records(
        tasks,
        solutions,
        calibration_ids,
        args.time_limit,
        args.maximum_candidates,
        analyzer,
    )
    families = sorted({record.candidate.family for record in records})
    preliminary = preliminary_calibration(records, families, args.prior_strength)
    accumulator = CalibrationAccumulator()
    for record in records:
        accumulator.add(
            record.candidate,
            record.metrics,
            record.task_state,
            record.success_fraction,
            families,
            preliminary,
        )
    metadata = {
        "source_split": "ARC-AGI-2 public training only",
        "holdout_policy": "deterministic task-id hash split",
        "holdout_fraction": args.holdout_fraction,
        "calibration_task_count": len(calibration_ids),
        "locked_holdout_task_count": len(holdout_ids),
        "candidate_time_limit": args.time_limit,
        "maximum_candidates_per_task": args.maximum_candidates,
        "reliability_target": "Jeffreys-smoothed held-out success log odds",
        "reliability_target_smoothing": {"success_pseudocount": 0.05, "total_pseudocount": 0.10},
        "feature_standardization": "center and scale with explicit uncentered bias",
        "collection": collection_report,
    }
    calibration = accumulator.finalize(families, metadata, prior_strength=args.prior_strength)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(calibration.to_json(), indent=2), encoding="utf-8")
    print(f"wrote calibration: {output}")

    model = BayesianProjectorResolvedLargeSignalModel(calibration=calibration, analyzer=ARCAtlasAnalyzer())
    calibration_evaluation = evaluate_model(model, tasks, solutions, calibration_ids, args.time_limit)
    holdout_evaluation = evaluate_model(model, tasks, solutions, holdout_ids, args.time_limit)
    report = {
        "model_version": calibration.model_version,
        "calibration_path": str(output),
        "training_metadata": metadata,
        "families": families,
        "family_priors": {name: prior.to_json() for name, prior in calibration.family_priors.items()},
        "calibration_evaluation": calibration_evaluation,
        "locked_training_holdout_evaluation": holdout_evaluation,
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "calibration": calibration_evaluation,
        "locked_training_holdout": holdout_evaluation,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
