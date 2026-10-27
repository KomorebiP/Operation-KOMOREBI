#!/usr/bin/env python3
from __future__ import annotations

import argparse
from hashlib import blake2b
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_arc2 import entry
from komorebi_arc2.lasm_bayesian import BayesianProjectorResolvedLargeSignalModel, load_calibration


def is_holdout(task_id: str, fraction: float) -> bool:
    digest = blake2b(task_id.encode("ascii"), digest_size=8, person=b"ARC2-LASM-split").digest()
    return int.from_bytes(digest, "big") / float(2**64) < fraction


def exact_output(candidate, index: int, answer) -> bool:
    return index < len(candidate.grids) and entry.exact(entry.as_array(candidate.grids[index]), entry.as_array(answer))


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Bayesian and deterministic selection on the fixed public-training holdout")
    parser.add_argument("--challenges", required=True)
    parser.add_argument("--solutions", required=True)
    parser.add_argument("--calibration", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--holdout-fraction", type=float, default=0.20)
    parser.add_argument("--time-limit", type=float, default=0.05)
    args = parser.parse_args()

    tasks = entry.load_tasks_from_path(args.challenges)
    solutions = entry.load_solutions_from_path(args.solutions)
    task_ids = [task_id for task_id in tasks if is_holdout(task_id, args.holdout_fraction)]
    model = BayesianProjectorResolvedLargeSignalModel(load_calibration(args.calibration))

    total = 0
    bayesian_correct = 0
    deterministic_correct = 0
    oracle_correct = 0
    bayesian_only = []
    deterministic_only = []
    records = {}
    started = time.perf_counter()

    for number, task_id in enumerate(task_ids, 1):
        task = tasks[task_id]
        train = [(entry.as_array(pair["input"]), entry.as_array(pair["output"])) for pair in task.get("train", [])]
        tests = [entry.as_array(pair["input"]) for pair in task.get("test", [])]
        candidates = entry.prune_candidates_for_bayesian(
            entry.deduplicate_candidates(entry.collect_candidates(train, tests, time_limit=args.time_limit))
        )
        posterior = model.fit_posterior(candidates, train, tests)
        answers = solutions.get(task_id, [])
        output_records = []
        for index, answer in enumerate(answers):
            total += 1
            target = entry.as_array(answer)
            selected = model.select_output_posteriors(posterior, index, k=2)
            bayes_grids = [value.grid for value in selected]
            while len(bayes_grids) < 2:
                bayes_grids.append(tests[index].copy() if index < len(tests) else target.copy())
            deterministic_grids = entry.legacy_rank_predictions(candidates, index, k=2)
            bayes_hit = any(entry.exact(grid, target) for grid in bayes_grids[:2])
            deterministic_hit = any(entry.exact(grid, target) for grid in deterministic_grids[:2])
            oracle_hit = any(exact_output(candidate, index, answer) for candidate in candidates)
            bayesian_correct += int(bayes_hit)
            deterministic_correct += int(deterministic_hit)
            oracle_correct += int(oracle_hit)
            key = f"{task_id}[{index}]"
            if bayes_hit and not deterministic_hit:
                bayesian_only.append(key)
            if deterministic_hit and not bayes_hit:
                deterministic_only.append(key)
            output_records.append({
                "test_index": index,
                "bayesian_correct": bayes_hit,
                "deterministic_correct": deterministic_hit,
                "candidate_oracle_correct": oracle_hit,
                "bayesian_selected": [
                    {
                        "probability": value.probability,
                        "exact_fit_probability": value.exact_fit_probability,
                        "names": list(value.names),
                        "families": list(value.families),
                    }
                    for value in selected
                ],
                "deterministic_attempts": [entry.grid_to_list(grid) for grid in deterministic_grids[:2]],
            })
        records[task_id] = {
            "candidate_count": len(candidates),
            "exact_fit_candidate_count": sum(candidate.train_error == 0 for candidate in candidates),
            "outputs": output_records,
        }
        if number <= 3 or number % 50 == 0 or number == len(task_ids):
            print(
                f"[{number:4d}/{len(task_ids):4d}] {task_id} "
                f"bayesian={bayesian_correct}/{total} deterministic={deterministic_correct}/{total} "
                f"oracle={oracle_correct}/{total} elapsed={time.perf_counter()-started:.1f}s",
                flush=True,
            )

    report = {
        "model_version": model.calibration.model_version,
        "partition": "deterministic public-training parameter holdout",
        "tasks": len(task_ids),
        "outputs_total": total,
        "bayesian_outputs_correct": bayesian_correct,
        "bayesian_score": bayesian_correct / max(1, total),
        "deterministic_outputs_correct": deterministic_correct,
        "deterministic_score": deterministic_correct / max(1, total),
        "candidate_oracle_outputs_correct": oracle_correct,
        "candidate_oracle_score": oracle_correct / max(1, total),
        "bayesian_only": bayesian_only,
        "deterministic_only": deterministic_only,
        "net_bayesian_gain": bayesian_correct - deterministic_correct,
        "elapsed_seconds": time.perf_counter() - started,
        "per_task": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "per_task"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
