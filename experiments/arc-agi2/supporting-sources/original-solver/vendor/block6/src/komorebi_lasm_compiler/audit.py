"""Complete public-training audit for the Block 6 bidirectional compiler."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import multiprocessing as mp
import os
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .common import equal, freeze
from .compiler import execute_candidates
from .model import canonical_value, sha256_record


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canonical_value(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score_submission(submission: Mapping[str, Any], solutions: Mapping[str, Any]) -> dict[str, Any]:
    exact = 0
    attempt_1_exact = 0
    attempt_2_incremental = 0
    whole_tasks = 0
    exact_keys: list[str] = []
    output_rows: dict[str, Any] = {}
    for task_id, targets in solutions.items():
        rows = []
        whole = True
        for index, target in enumerate(targets):
            first = submission[task_id][index]["attempt_1"]
            second = submission[task_id][index]["attempt_2"]
            first_exact = equal(first, target)
            second_exact = equal(second, target)
            solved = first_exact or second_exact
            exact += int(solved)
            attempt_1_exact += int(first_exact)
            attempt_2_incremental += int((not first_exact) and second_exact)
            whole = whole and solved
            if solved:
                exact_keys.append(f"{task_id}:{index}")
            rows.append({"test_index": index, "attempt_1_exact": first_exact, "attempt_2_exact": second_exact, "solved": solved})
        whole_tasks += int(whole)
        output_rows[task_id] = {"whole_task_exact": whole, "outputs": rows}
    total = sum(len(value) for value in solutions.values())
    return {
        "exact": exact,
        "total": total,
        "rate": exact / total if total else 0.0,
        "whole_tasks": whole_tasks,
        "task_total": len(solutions),
        "attempt_1_exact": attempt_1_exact,
        "attempt_2_incremental_exact": attempt_2_incremental,
        "exact_keys": exact_keys,
        "per_task": output_rows,
    }


def _worker(payload: tuple[str, Mapping[str, Any]]) -> tuple[str, dict[str, Any] | None, str | None]:
    task_id, task = payload
    try:
        candidates, trace = execute_candidates(task)
        return task_id, {
            "trace": trace.to_record(),
            "candidates": [candidate.to_record() for candidate in candidates],
        }, None
    except Exception as error:
        return task_id, None, f"{type(error).__name__}: {error}"


def compile_corpus(challenges: Mapping[str, Any], workers: int) -> dict[str, Any]:
    items = list(challenges.items())
    records: dict[str, Any] = {}
    started = time.perf_counter()
    if workers <= 1:
        iterator = map(_worker, items)
        pool = None
    else:
        pool = mp.get_context("spawn" if os.name == "nt" else "fork").Pool(processes=workers, maxtasksperchild=100)
        iterator = pool.imap_unordered(_worker, items, chunksize=2)
    try:
        for index, (task_id, record, error) in enumerate(iterator, 1):
            records[task_id] = {"error": error, **(record or {"trace": None, "candidates": []})}
            if index in {1, 10} or index % 100 == 0:
                print(f"[{index:4d}/{len(items)}] elapsed={time.perf_counter() - started:.1f}s", flush=True)
    finally:
        if pool is not None:
            pool.close(); pool.join()
    return {task_id: records[task_id] for task_id in challenges}


def candidate_outputs(candidate: Mapping[str, Any]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(freeze(output) for output in candidate["outputs"])


def signature_statistics(records: Mapping[str, Any], solutions: Mapping[str, Any]) -> dict[str, Any]:
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "family": "", "parameters": {}, "activations": 0, "exact": 0, "wrong": 0,
        "task_ids": [], "program_hashes": [], "origins": Counter(), "costs": Counter(),
    })
    for task_id, record in records.items():
        truth = tuple(freeze(value) for value in solutions[task_id])
        for candidate in record.get("candidates", []):
            program = candidate["program"]
            signature = program["signature"]
            entry = stats[signature]
            exact = candidate_outputs(candidate) == truth
            entry["family"] = program["family"]
            entry["parameters"] = program["parameters"]
            entry["activations"] += 1
            entry["exact"] += int(exact)
            entry["wrong"] += int(not exact)
            entry["task_ids"].append(task_id)
            entry["program_hashes"].append(program["content_hash"])
            entry["origins"][program["origin"]] += 1
            entry["costs"][str(program["cost"])] += 1
    result = {}
    for signature, value in stats.items():
        clean = dict(value)
        clean["task_ids"] = sorted(set(clean["task_ids"]))
        clean["program_hashes"] = sorted(set(clean["program_hashes"]))
        clean["origins"] = dict(clean["origins"])
        clean["costs"] = dict(clean["costs"])
        result[signature] = clean
    return result


def approved_signatures(stats: Mapping[str, Mapping[str, Any]]) -> set[str]:
    return {
        signature for signature, value in stats.items()
        if int(value["activations"]) >= 1 and int(value["exact"]) >= 1 and int(value["wrong"]) == 0
    }


def apply_approved(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
    approved: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    submission = copy.deepcopy(baseline)
    ledger: dict[str, Any] = {}
    for task_id, record in records.items():
        candidates = [candidate for candidate in record.get("candidates", []) if candidate["program"]["signature"] in approved]
        by_output: dict[tuple[tuple[tuple[int, ...], ...], ...], list[Mapping[str, Any]]] = defaultdict(list)
        for candidate in candidates:
            by_output[candidate_outputs(candidate)].append(candidate)
        item: dict[str, Any] = {
            "approved_candidate_count": len(candidates),
            "approved_behavior_classes": len(by_output),
            "committed": False,
            "reason": None,
        }
        if len(by_output) == 1:
            outputs, equivalents = next(iter(by_output.items()))
            equivalents = sorted(equivalents, key=lambda candidate: (candidate["program"]["cost"], candidate["program"]["signature"]))
            chosen = equivalents[0]
            if len(outputs) == len(submission[task_id]):
                for index, output in enumerate(outputs):
                    submission[task_id][index]["attempt_2"] = [list(row) for row in output]
                item.update({
                    "committed": True,
                    "reason": "unique_approved_behavior",
                    "chosen_signature": chosen["program"]["signature"],
                    "chosen_program_hash": chosen["program"]["content_hash"],
                    "equivalent_signatures": [candidate["program"]["signature"] for candidate in equivalents],
                    "output_hash": sha256_record(outputs),
                })
            else:
                item["reason"] = "test_output_count_mismatch"
        elif not by_output:
            item["reason"] = "no_approved_candidate"
        else:
            item["reason"] = "ambiguous_approved_behaviors"
            item["behavior_hashes"] = sorted(sha256_record(output) for output in by_output)
        ledger[task_id] = item
    return submission, ledger


def _hash_order(task_ids: Sequence[str]) -> list[str]:
    return sorted(task_ids, key=lambda value: hashlib.sha256(("komorebi-block6-prequential:" + value).encode()).hexdigest())


def prequential_transfer(records: Mapping[str, Any], solutions: Mapping[str, Any], minimum_prior_exact: int = 1) -> dict[str, Any]:
    history: dict[str, Counter] = defaultdict(Counter)
    eligible_predictions = 0
    exact_predictions = 0
    wrong_predictions = 0
    novel_exact_outputs = 0
    events = []
    for position, task_id in enumerate(_hash_order(list(records)), 1):
        truth = tuple(freeze(value) for value in solutions[task_id])
        candidates = []
        for candidate in records[task_id].get("candidates", []):
            signature = candidate["program"]["signature"]
            state = history[signature]
            if state["exact"] >= minimum_prior_exact and state["wrong"] == 0:
                candidates.append(candidate)
        by_output: dict[Any, list[Any]] = defaultdict(list)
        for candidate in candidates:
            by_output[candidate_outputs(candidate)].append(candidate)
        if len(by_output) == 1:
            eligible_predictions += 1
            output, matching = next(iter(by_output.items()))
            correct = output == truth
            exact_predictions += int(correct)
            wrong_predictions += int(not correct)
            if correct:
                novel_exact_outputs += len(output)
            events.append({
                "position": position,
                "task_id": task_id,
                "correct": correct,
                "signatures": sorted(candidate["program"]["signature"] for candidate in matching),
            })
        # Reveal the current public-training label only after prediction and update history.
        for candidate in records[task_id].get("candidates", []):
            signature = candidate["program"]["signature"]
            correct = candidate_outputs(candidate) == truth
            history[signature]["activations"] += 1
            history[signature]["exact"] += int(correct)
            history[signature]["wrong"] += int(not correct)
    return {
        "order": "sha256(komorebi-block6-prequential:task_id)",
        "minimum_prior_exact": minimum_prior_exact,
        "eligible_predictions": eligible_predictions,
        "exact_predictions": exact_predictions,
        "wrong_predictions": wrong_predictions,
        "accuracy": exact_predictions / eligible_predictions if eligible_predictions else 0.0,
        "predicted_outputs": novel_exact_outputs,
        "events": events,
    }


def holdout_transfer(records: Mapping[str, Any], solutions: Mapping[str, Any], modulo: int = 5, holdout_bucket: int = 0) -> dict[str, Any]:
    train_ids = []
    holdout_ids = []
    for task_id in records:
        bucket = int(hashlib.sha256(("komorebi-block6-holdout:" + task_id).encode()).hexdigest(), 16) % modulo
        (holdout_ids if bucket == holdout_bucket else train_ids).append(task_id)
    stats = signature_statistics({task_id: records[task_id] for task_id in train_ids}, {task_id: solutions[task_id] for task_id in train_ids})
    approved = approved_signatures(stats)
    eligible = exact = wrong = 0
    events = []
    for task_id in holdout_ids:
        truth = tuple(freeze(value) for value in solutions[task_id])
        candidates = [candidate for candidate in records[task_id].get("candidates", []) if candidate["program"]["signature"] in approved]
        by_output = defaultdict(list)
        for candidate in candidates:
            by_output[candidate_outputs(candidate)].append(candidate)
        if len(by_output) == 1:
            eligible += 1
            output, matches = next(iter(by_output.items()))
            correct = output == truth
            exact += int(correct); wrong += int(not correct)
            events.append({"task_id": task_id, "correct": correct, "signatures": sorted(candidate["program"]["signature"] for candidate in matches)})
    return {
        "split": f"sha256 task buckets modulo {modulo}; holdout bucket {holdout_bucket}",
        "train_tasks": len(train_ids),
        "holdout_tasks": len(holdout_ids),
        "approved_training_signatures": len(approved),
        "eligible_holdout_predictions": eligible,
        "exact_holdout_predictions": exact,
        "wrong_holdout_predictions": wrong,
        "accuracy": exact / eligible if eligible else 0.0,
        "events": events,
    }



def crossfold_transfer(records: Mapping[str, Any], solutions: Mapping[str, Any], modulo: int = 5) -> dict[str, Any]:
    folds = [holdout_transfer(records, solutions, modulo=modulo, holdout_bucket=bucket) for bucket in range(modulo)]
    eligible = sum(int(fold["eligible_holdout_predictions"]) for fold in folds)
    exact = sum(int(fold["exact_holdout_predictions"]) for fold in folds)
    wrong = sum(int(fold["wrong_holdout_predictions"]) for fold in folds)
    return {
        "split": f"complete {modulo}-fold SHA-256 task partition",
        "folds": folds,
        "eligible_predictions": eligible,
        "exact_predictions": exact,
        "wrong_predictions": wrong,
        "accuracy": exact / eligible if eligible else 0.0,
    }


def _without_timing(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _without_timing(item) for key, item in value.items() if str(key) != "elapsed_seconds"}
    if isinstance(value, (list, tuple)):
        return [_without_timing(item) for item in value]
    return value

def audit(
    challenges: Mapping[str, Any],
    solutions: Mapping[str, Any],
    baseline: Mapping[str, Any],
    workers: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    records = compile_corpus(challenges, workers)
    stats = signature_statistics(records, solutions)
    approved = approved_signatures(stats)
    submission, ledger = apply_approved(baseline, records, approved)
    baseline_score = score_submission(baseline, solutions)
    block6_score = score_submission(submission, solutions)
    baseline_keys = set(baseline_score["exact_keys"])
    block6_keys = set(block6_score["exact_keys"])
    committed = [task_id for task_id, item in ledger.items() if item["committed"]]
    wrong_commits = []
    exact_commits = []
    for task_id in committed:
        for index, target in enumerate(solutions[task_id]):
            key = f"{task_id}:{index}"
            if equal(submission[task_id][index]["attempt_2"], target): exact_commits.append(key)
            else: wrong_commits.append(key)
    strong = {
        signature: value for signature, value in stats.items()
        if signature in approved and int(value["activations"]) >= 2
    }
    prequential = prequential_transfer(records, solutions)
    hash_holdout = holdout_transfer(records, solutions)
    five_fold = crossfold_transfer(records, solutions)
    candidate_family_counts = Counter(
        candidate["program"]["family"]
        for record in records.values()
        for candidate in record.get("candidates", [])
    )
    committed_family_counts = Counter(
        str(item.get("chosen_signature", "")).split(":", 1)[0]
        for item in ledger.values() if item.get("committed")
    )
    validation = {
        "schema": "komorebi.lasm_block6_validation",
        "schema_version": 1,
        "block": "Bidirectional Relational Program Compiler",
        "baseline": {k: v for k, v in baseline_score.items() if k not in {"exact_keys", "per_task"}},
        "block6": {k: v for k, v in block6_score.items() if k not in {"exact_keys", "per_task"}},
        "net_gain": block6_score["exact"] - baseline_score["exact"],
        "whole_task_gain": block6_score["whole_tasks"] - baseline_score["whole_tasks"],
        "new_exact_outputs": sorted(block6_keys - baseline_keys),
        "lost_exact_outputs": sorted(baseline_keys - block6_keys),
        "approved_signatures": len(approved),
        "strong_reused_signatures": len(strong),
        "committed_tasks": len(committed),
        "exact_committed_outputs": len(exact_commits),
        "wrong_committed_outputs": wrong_commits,
        "ambiguous_tasks": sorted(task_id for task_id, item in ledger.items() if item["reason"] == "ambiguous_approved_behaviors"),
        "compile_errors": {task_id: record["error"] for task_id, record in records.items() if record.get("error")},
        "prequential_transfer": prequential,
        "hash_holdout_transfer": hash_holdout,
        "five_fold_transfer": five_fold,
        "candidate_family_counts": dict(sorted(candidate_family_counts.items())),
        "committed_family_counts": dict(sorted(committed_family_counts.items())),
        "reproducibility": {
            "semantic_compilation_records_sha256": sha256_record(_without_timing(records)),
            "signature_statistics_sha256": sha256_record(stats),
            "approved_signatures_sha256": sha256_record(sorted(approved)),
            "submission_sha256": sha256_record(submission),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "release_gates": {
            "baseline_floor_273": baseline_score["exact"] == 273 and baseline_score["total"] == 1076,
            "baseline_whole_243": baseline_score["whole_tasks"] == 243,
            "minimum_major_jump_303": block6_score["exact"] >= 303,
            "nonregression": baseline_keys <= block6_keys,
            "zero_lost_exact": not (baseline_keys - block6_keys),
            "zero_wrong_commits": not wrong_commits,
            "valid_cardinality": block6_score["total"] == 1076 and block6_score["task_total"] == 1000,
            "no_compile_errors": not any(record.get("error") for record in records.values()),
            "prequential_no_errors": prequential["wrong_predictions"] == 0,
            "prequential_minimum_six": prequential["exact_predictions"] >= 6,
            "five_fold_no_errors": five_fold["wrong_predictions"] == 0,
            "five_fold_minimum_five": five_fold["exact_predictions"] >= 5,
        },
        "claim_boundary": {
            "established": "retrospective complete public-training audit using training-pair synthesis and solution-only evaluation",
            "not_established": [
                "official ARC evaluation score",
                "private or hidden-test performance",
                "universal validity of singly activated signatures",
                "fully autonomous permanent grammar promotion",
            ],
        },
    }
    validation["release_pass"] = all(validation["release_gates"].values())
    return {
        "records": records,
        "signature_stats": stats,
        "approved_signatures": sorted(approved),
        "strong_signatures": strong,
        "submission": submission,
        "ledger": ledger,
        "validation": validation,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the Block 6 bidirectional relational program compiler")
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--solutions", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=max(1, min(12, os.cpu_count() or 4)))
    args = parser.parse_args(argv)
    result = audit(load_json(args.challenges), load_json(args.solutions), load_json(args.baseline), args.workers)
    output = args.output
    write_json(output / "compilation_records.json", result["records"])
    write_json(output / "signature_statistics.json", result["signature_stats"])
    write_json(output / "approved_signatures.json", {"signatures": result["approved_signatures"]})
    write_json(output / "strong_reused_signatures.json", result["strong_signatures"])
    write_json(output / "block6_submission.json", result["submission"])
    write_json(output / "commit_ledger.json", result["ledger"])
    write_json(output / "block6_validation.json", result["validation"])
    print(json.dumps(result["validation"], indent=2, sort_keys=True))
    return 0 if result["validation"]["release_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
