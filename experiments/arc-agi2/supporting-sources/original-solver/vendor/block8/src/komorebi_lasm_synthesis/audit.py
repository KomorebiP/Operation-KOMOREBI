"""Complete retrospective audit and prospective transfer tests for Block 8."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import multiprocessing as mp
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.audit import score_submission
from komorebi_lasm_compiler.common import equal, freeze
from komorebi_lasm_compiler.model import canonical_value, sha256_record

from .bank import build_schema_evidence
from .compiler import compile_record
from .families import DEFINITIONS, SCHEMA_FAMILIES, family_sketches


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canonical_value(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def candidate_outputs(candidate: Mapping[str, Any]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(freeze(output) for output in candidate["outputs"])


def candidate_correct(candidate: Mapping[str, Any], targets: Sequence[Any]) -> bool:
    return candidate_outputs(candidate) == tuple(freeze(target) for target in targets)


def _worker(payload: tuple[str, Mapping[str, Any]]) -> tuple[str, dict[str, Any] | None, str | None]:
    task_id, task = payload
    try:
        sanitized = {
            "train": [{"input": item["input"], "output": item["output"]} for item in task.get("train", [])],
            "test": [{"input": item["input"]} for item in task.get("test", [])],
        }
        return task_id, compile_record(sanitized), None
    except Exception as error:
        return task_id, None, f"{type(error).__name__}: {error}"


def compile_corpus(challenges: Mapping[str, Any], workers: int = 1) -> dict[str, Any]:
    items = list(challenges.items())
    records: dict[str, Any] = {}
    started = time.perf_counter()
    if workers <= 1:
        iterator = map(_worker, items)
        pool = None
    else:
        context = mp.get_context("spawn" if os.name == "nt" else "fork")
        pool = context.Pool(processes=workers, maxtasksperchild=100)
        iterator = pool.imap_unordered(_worker, items, chunksize=2)
    try:
        for index, (task_id, record, error) in enumerate(iterator, 1):
            records[task_id] = {**(record or {"obstruction": None, "trace": None, "candidates": []}), "error": error}
            if index in {1, 10} or index % 100 == 0:
                print(f"[{index:4d}/{len(items)}] elapsed={time.perf_counter() - started:.1f}s", flush=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    return {task_id: records[task_id] for task_id in challenges}


def family_statistics(records: Mapping[str, Any], solutions: Mapping[str, Any]) -> dict[str, Any]:
    state: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "macro_schema": "", "activations": 0, "exact": 0, "wrong": 0,
        "task_ids": [], "exact_task_ids": [], "wrong_task_ids": [], "signature_hashes": set(),
    })
    for task_id, record in records.items():
        for candidate in record.get("candidates", []):
            program = candidate["program"]
            family = str(program["family"])
            item = state[family]
            correct = candidate_correct(candidate, solutions[task_id])
            item["macro_schema"] = str(program["macro_schema"])
            item["activations"] += 1
            item["exact"] += int(correct)
            item["wrong"] += int(not correct)
            item["task_ids"].append(task_id)
            item["signature_hashes"].add(str(program["signature_hash"]))
            (item["exact_task_ids"] if correct else item["wrong_task_ids"]).append(task_id)
    result = {}
    for definition in DEFINITIONS:
        value = state[definition.name]
        result[definition.name] = {
            "family": definition.name,
            "macro_schema": definition.macro_schema,
            "activations": int(value["activations"]),
            "exact": int(value["exact"]),
            "wrong": int(value["wrong"]),
            "task_ids": sorted(set(value["task_ids"])),
            "exact_task_ids": sorted(set(value["exact_task_ids"])),
            "wrong_task_ids": sorted(set(value["wrong_task_ids"])),
            "signature_hashes": sorted(value["signature_hashes"]),
        }
    return result


def approved_families(statistics: Mapping[str, Mapping[str, Any]]) -> set[str]:
    return {
        family for family, value in statistics.items()
        if int(value["activations"]) >= 1 and int(value["exact"]) >= 1 and int(value["wrong"]) == 0
    }


def _unique_behavior(candidates: Sequence[Mapping[str, Any]]) -> tuple[Any | None, list[Mapping[str, Any]], int]:
    by_output: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_output[candidate_outputs(candidate)].append(candidate)
    if len(by_output) != 1:
        return None, [], len(by_output)
    output, matches = next(iter(by_output.items()))
    return output, matches, 1


def apply_approved(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
    approved: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    submission = copy.deepcopy(baseline)
    ledger = {}
    for task_id, record in records.items():
        candidates = [candidate for candidate in record.get("candidates", []) if candidate["program"]["family"] in approved]
        output, matches, behavior_count = _unique_behavior(candidates)
        item = {
            "approved_candidates": len(candidates),
            "behavior_classes": behavior_count,
            "committed": False,
            "reason": "no_approved_candidate" if not candidates else "ambiguous_approved_behaviors",
        }
        if output is not None and len(output) == len(submission[task_id]):
            matches = sorted(matches, key=lambda candidate: (candidate["program"]["cost"], candidate["program"]["signature_hash"]))
            for index, grid in enumerate(output):
                submission[task_id][index]["attempt_2"] = [list(row) for row in grid]
            item.update({
                "committed": True,
                "reason": "unique_approved_behavior",
                "chosen_family": matches[0]["program"]["family"],
                "chosen_schema": matches[0]["program"]["macro_schema"],
                "chosen_signature_hash": matches[0]["program"]["signature_hash"],
                "equivalent_signature_hashes": sorted(candidate["program"]["signature_hash"] for candidate in matches),
                "output_hash": sha256_record(output),
            })
        ledger[task_id] = item
    return submission, ledger


def _hash_order(task_ids: Iterable[str], salt: str) -> list[str]:
    return sorted(task_ids, key=lambda task_id: hashlib.sha256((salt + task_id).encode("utf-8")).hexdigest())


def _matching_schema_candidates(record: Mapping[str, Any], schemas: set[str]) -> list[Mapping[str, Any]]:
    return [candidate for candidate in record.get("candidates", []) if candidate["program"]["macro_schema"] in schemas]


def prequential_schema_transfer(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    minimum_support: int,
    salt: str,
    include_events: bool = True,
) -> dict[str, Any]:
    evidence: dict[str, dict[str, Any]] = defaultdict(lambda: {"exact_tasks": set(), "wrong": 0})
    eligible = exact = wrong = outputs = 0
    events = []
    for position, task_id in enumerate(_hash_order(records, salt), 1):
        active = {schema for schema, state in evidence.items() if len(state["exact_tasks"]) >= minimum_support and state["wrong"] == 0}
        candidates = _matching_schema_candidates(records[task_id], active)
        output, matches, _ = _unique_behavior(candidates)
        if output is not None:
            correct = output == tuple(freeze(value) for value in solutions[task_id])
            eligible += 1
            exact += int(correct)
            wrong += int(not correct)
            outputs += len(output)
            if include_events:
                events.append({
                    "position": position,
                    "task_id": task_id,
                    "correct": correct,
                    "macro_schemas": sorted({candidate["program"]["macro_schema"] for candidate in matches}),
                    "families": sorted({candidate["program"]["family"] for candidate in matches}),
                })
        # Reveal labels only after the prospective prediction.
        for candidate in records[task_id].get("candidates", []):
            schema = candidate["program"]["macro_schema"]
            if candidate_correct(candidate, solutions[task_id]):
                evidence[schema]["exact_tasks"].add(task_id)
            else:
                evidence[schema]["wrong"] += 1
    return {
        "order": f"sha256({salt}task_id)",
        "minimum_prior_exact_tasks": minimum_support,
        "eligible_predictions": eligible,
        "exact_predictions": exact,
        "wrong_predictions": wrong,
        "predicted_outputs": outputs,
        "accuracy": exact / eligible if eligible else 0.0,
        "events": events if include_events else [],
    }


def exact_signature_prequential(records: Mapping[str, Any], solutions: Mapping[str, Any], *, salt: str) -> dict[str, Any]:
    evidence: dict[str, Counter] = defaultdict(Counter)
    eligible = exact = wrong = 0
    events = []
    for position, task_id in enumerate(_hash_order(records, salt), 1):
        candidates = [
            candidate for candidate in records[task_id].get("candidates", [])
            if evidence[candidate["program"]["signature_hash"]]["exact"] >= 1
            and evidence[candidate["program"]["signature_hash"]]["wrong"] == 0
        ]
        output, matches, _ = _unique_behavior(candidates)
        if output is not None:
            correct = output == tuple(freeze(value) for value in solutions[task_id])
            eligible += 1; exact += int(correct); wrong += int(not correct)
            events.append({"position": position, "task_id": task_id, "correct": correct})
        for candidate in records[task_id].get("candidates", []):
            state = evidence[candidate["program"]["signature_hash"]]
            correct = candidate_correct(candidate, solutions[task_id])
            state["exact"] += int(correct)
            state["wrong"] += int(not correct)
    return {"eligible_predictions": eligible, "exact_predictions": exact, "wrong_predictions": wrong, "events": events}


def fold_schema_transfer(
    records: Mapping[str, Any], solutions: Mapping[str, Any], *, minimum_support: int, salt: str, modulo: int = 5
) -> dict[str, Any]:
    folds = []
    totals = Counter()
    for bucket in range(modulo):
        train_ids, holdout_ids = [], []
        for task_id in sorted(records):
            value = int(hashlib.sha256((salt + task_id).encode("utf-8")).hexdigest(), 16) % modulo
            (holdout_ids if value == bucket else train_ids).append(task_id)
        evidence: dict[str, dict[str, Any]] = defaultdict(lambda: {"exact_tasks": set(), "wrong": 0})
        for task_id in train_ids:
            for candidate in records[task_id].get("candidates", []):
                schema = candidate["program"]["macro_schema"]
                if candidate_correct(candidate, solutions[task_id]):
                    evidence[schema]["exact_tasks"].add(task_id)
                else:
                    evidence[schema]["wrong"] += 1
        active = {schema for schema, state in evidence.items() if len(state["exact_tasks"]) >= minimum_support and state["wrong"] == 0}
        eligible = exact = wrong = outputs = 0
        events = []
        for task_id in holdout_ids:
            output, matches, _ = _unique_behavior(_matching_schema_candidates(records[task_id], active))
            if output is None:
                continue
            correct = output == tuple(freeze(value) for value in solutions[task_id])
            eligible += 1; exact += int(correct); wrong += int(not correct); outputs += len(output)
            events.append({"task_id": task_id, "correct": correct, "macro_schemas": sorted({c["program"]["macro_schema"] for c in matches})})
        fold = {
            "holdout_bucket": bucket, "train_tasks": len(train_ids), "holdout_tasks": len(holdout_ids),
            "active_schemas": len(active), "eligible_predictions": eligible,
            "exact_predictions": exact, "wrong_predictions": wrong, "predicted_outputs": outputs,
            "events": events,
        }
        folds.append(fold)
        totals.update({"eligible": eligible, "exact": exact, "wrong": wrong, "outputs": outputs})
    return {
        "split": f"complete {modulo}-fold SHA-256 task partition",
        "minimum_training_exact_tasks": minimum_support,
        "eligible_predictions": totals["eligible"],
        "exact_predictions": totals["exact"],
        "wrong_predictions": totals["wrong"],
        "predicted_outputs": totals["outputs"],
        "folds": folds,
    }


def audit(
    challenges: Mapping[str, Any], solutions: Mapping[str, Any], baseline: Mapping[str, Any], *, workers: int = 1
) -> dict[str, Any]:
    started = time.perf_counter()
    records = compile_corpus(challenges, workers=workers)
    statistics = family_statistics(records, solutions)
    approved = approved_families(statistics)
    schema_audit, runtime_bank = build_schema_evidence(records, solutions, minimum_support=2)
    submission, overlay_ledger = apply_approved(baseline, records, approved)
    baseline_score = score_submission(baseline, solutions)
    score = score_submission(submission, solutions)
    baseline_keys = set(baseline_score["exact_keys"])
    current_keys = set(score["exact_keys"])
    exact_commits = []
    wrong_commits = []
    for task_id, item in overlay_ledger.items():
        if not item.get("committed"):
            continue
        for index, target in enumerate(solutions[task_id]):
            key = f"{task_id}:{index}"
            if equal(submission[task_id][index]["attempt_2"], target):
                exact_commits.append(key)
            else:
                wrong_commits.append(key)
    stable_count = sum(value["status"] == "stable" for value in runtime_bank["macros"])
    provisional_count = sum(value["status"] == "provisional" for value in runtime_bank["macros"])
    prequential_stable = prequential_schema_transfer(records, solutions, minimum_support=2, salt="komorebi-block8-prequential-stable:")
    prequential_provisional = prequential_schema_transfer(records, solutions, minimum_support=1, salt="komorebi-block8-prequential-provisional:")
    signature_baseline = exact_signature_prequential(records, solutions, salt="komorebi-block8-prequential-provisional:")
    five_fold_stable = fold_schema_transfer(records, solutions, minimum_support=2, salt="komorebi-block8-fivefold-stable:")
    five_fold_provisional = fold_schema_transfer(records, solutions, minimum_support=1, salt="komorebi-block8-fivefold-provisional:")
    runtime_task_ids = []
    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for item in value.values(): visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
        elif isinstance(value, str) and re.fullmatch(r"[0-9a-f]{8}", value):
            runtime_task_ids.append(value)
    visit(runtime_bank)
    obstruction_packets = {task_id: record.get("obstruction") for task_id, record in records.items()}
    validation = {
        "schema": "komorebi.lasm_block8_validation",
        "schema_version": 1,
        "block": "Obstruction-Guided Macro Synthesis",
        "baseline": {k: v for k, v in baseline_score.items() if k not in {"exact_keys", "per_task"}},
        "block8": {k: v for k, v in score.items() if k not in {"exact_keys", "per_task"}},
        "net_gain": score["exact"] - baseline_score["exact"],
        "whole_task_gain": score["whole_tasks"] - baseline_score["whole_tasks"],
        "new_exact_outputs": sorted(current_keys - baseline_keys),
        "lost_exact_outputs": sorted(baseline_keys - current_keys),
        "exact_committed_outputs": sorted(exact_commits),
        "wrong_committed_outputs": sorted(wrong_commits),
        "approved_families": sorted(approved),
        "family_statistics": statistics,
        "stable_schema_count": stable_count,
        "provisional_schema_count": provisional_count,
        "runtime_bank_id": runtime_bank["bank_id"],
        "runtime_task_id_literals": sorted(runtime_task_ids),
        "tasks_with_candidates": sum(bool(record.get("candidates")) for record in records.values()),
        "candidate_count": sum(len(record.get("candidates", [])) for record in records.values()),
        "behavior_class_count": sum(int((record.get("trace") or {}).get("behavior_classes", 0)) for record in records.values()),
        "compile_errors": {task_id: record["error"] for task_id, record in records.items() if record.get("error")},
        "prequential_stable": prequential_stable,
        "prequential_provisional": prequential_provisional,
        "exact_signature_baseline": signature_baseline,
        "five_fold_stable": five_fold_stable,
        "five_fold_provisional": five_fold_provisional,
        "reproducibility": {
            "records_sha256": sha256_record(records),
            "obstruction_packets_sha256": sha256_record(obstruction_packets),
            "family_statistics_sha256": sha256_record(statistics),
            "schema_evidence_sha256": sha256_record(schema_audit),
            "runtime_bank_sha256": sha256_record(runtime_bank),
            "submission_sha256": sha256_record(submission),
            "overlay_ledger_sha256": sha256_record(overlay_ledger),
        },
        "elapsed_seconds": 0.0,
        "release_gates": {
            "baseline_floor_306": baseline_score["exact"] == 306 and baseline_score["total"] == 1076,
            "baseline_whole_276": baseline_score["whole_tasks"] == 276,
            "block8_floor_318": score["exact"] >= 318,
            "block8_whole_288": score["whole_tasks"] >= 288,
            "nonregression": baseline_keys <= current_keys,
            "zero_lost_exact": not (baseline_keys - current_keys),
            "zero_wrong_commits": not wrong_commits,
            "minimum_ten_approved_families": len(approved) >= 10,
            "minimum_five_stable_schemas": stable_count >= 5,
            "minimum_four_provisional_schemas": provisional_count >= 4,
            "runtime_bank_task_id_free": not runtime_task_ids,
            "compile_error_free": not any(record.get("error") for record in records.values()),
            "stable_transfer_zero_wrong": prequential_stable["wrong_predictions"] == 0 and five_fold_stable["wrong_predictions"] == 0,
            "provisional_transfer_zero_wrong": prequential_provisional["wrong_predictions"] == 0 and five_fold_provisional["wrong_predictions"] == 0,
            "valid_cardinality": score["total"] == 1076 and score["task_total"] == 1000,
        },
        "claim_boundary": {
            "established": [
                "retrospective complete public-training portfolio score",
                "training-only obstruction packets and finite macro hole filling",
                "exact demonstration replay and Program IR v2 execution agreement",
                "task-ID-free stable and provisional macro-schema bank",
                "predict-before-label transfer experiments inside public training",
            ],
            "not_established": [
                "official ARC evaluation score",
                "private or hidden-test performance",
                "universal validity of provisional one-source macros",
                "universal macro synthesis",
                "cross-domain transfer",
            ],
        },
    }
    validation["release_pass"] = all(validation["release_gates"].values())
    return {
        "compilation_records": records,
        "obstruction_packets": obstruction_packets,
        "macro_sketches": {"sketches": [sketch.to_record() for sketch in family_sketches()]},
        "family_evidence": statistics,
        "schema_evidence": schema_audit,
        "runtime_macro_bank": runtime_bank,
        "submission": submission,
        "overlay_ledger": overlay_ledger,
        "validation": validation,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit PR-LASM Obstruction-Guided Macro Synthesis Block 8")
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--solutions", type=Path, required=True)
    parser.add_argument("--baseline-submission", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    args = parser.parse_args(argv)
    result = audit(load_json(args.challenges), load_json(args.solutions), load_json(args.baseline_submission), workers=args.workers)
    output = args.output
    write_json(output / "compilation_records.json", result["compilation_records"])
    write_json(output / "obstruction_packets.json", result["obstruction_packets"])
    write_json(output / "macro_sketches.json", result["macro_sketches"])
    write_json(output / "family_evidence.json", result["family_evidence"])
    write_json(output / "schema_evidence.json", result["schema_evidence"])
    write_json(output / "runtime_macro_bank.json", result["runtime_macro_bank"])
    write_json(output / "block8_submission.json", result["submission"])
    write_json(output / "overlay_ledger.json", result["overlay_ledger"])
    write_json(output / "prequential_stable.json", result["validation"]["prequential_stable"])
    write_json(output / "prequential_provisional.json", result["validation"]["prequential_provisional"])
    write_json(output / "five_fold_stable.json", result["validation"]["five_fold_stable"])
    write_json(output / "five_fold_provisional.json", result["validation"]["five_fold_provisional"])
    write_json(output / "block8_validation.json", result["validation"])
    print(json.dumps(result["validation"], indent=2, sort_keys=True))
    return 0 if result["validation"]["release_pass"] else 2


__all__ = [
    "apply_approved", "audit", "candidate_correct", "candidate_outputs", "compile_corpus",
    "exact_signature_prequential", "family_statistics", "fold_schema_transfer",
    "prequential_schema_transfer", "score_submission",
]


if __name__ == "__main__":
    raise SystemExit(main())
