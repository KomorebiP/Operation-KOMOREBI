"""Corpus audit, nonregressing overlay, and abstraction-closure evidence."""
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

from .abstraction import (
    PromotionStatus,
    SubtreeOccurrence,
    extract_contiguous_subtrees,
    semantic_subtree_schema,
)
from .bank import AbstractionEvidenceBank
from .compiler import DEFAULT_LIMITS, compile_record
from .model import canonical_value, sha256_record


SCHEMA = "komorebi.lasm_recursive_composition_audit"
SCHEMA_VERSION = 1

_WORKER_BLOCK6: Mapping[str, Any] | None = None
_WORKER_BLOCK8: Mapping[str, Any] | None = None
_WORKER_ABSTRACTION: Mapping[str, Any] | None = None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(canonical_value(value), indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _initialize_worker(
    block6: Mapping[str, Any] | None,
    block8: Mapping[str, Any] | None,
    abstraction: Mapping[str, Any] | None,
) -> None:
    global _WORKER_BLOCK6, _WORKER_BLOCK8, _WORKER_ABSTRACTION
    _WORKER_BLOCK6 = block6
    _WORKER_BLOCK8 = block8
    _WORKER_ABSTRACTION = abstraction


def _compile_worker(payload: tuple[str, Mapping[str, Any]]) -> tuple[str, dict[str, Any]]:
    task_id, task = payload
    try:
        record = compile_record(
            task,
            block6_bank_record=_WORKER_BLOCK6,
            block8_bank_record=_WORKER_BLOCK8,
            abstraction_bank=_WORKER_ABSTRACTION,
            limits=DEFAULT_LIMITS,
        )
        return task_id, {**record, "error": None}
    except Exception as error:  # audit must retain every failure, not drop tasks
        return task_id, {
            "schema": "komorebi.lasm_recursive_composition_record",
            "schema_version": 1,
            "trace": None,
            "candidates": [],
            "unique_test_behavior": False,
            "error": f"{type(error).__name__}: {error}",
        }


def compile_corpus(
    challenges: Mapping[str, Any],
    *,
    block6_bank_record: Mapping[str, Any],
    block8_bank_record: Mapping[str, Any],
    abstraction_bank_record: Mapping[str, Any] | None = None,
    workers: int = 1,
) -> dict[str, Any]:
    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    items = tuple((str(task_id), challenges[task_id]) for task_id in sorted(challenges))
    records: dict[str, Any] = {}
    if workers == 1:
        _initialize_worker(block6_bank_record, block8_bank_record, abstraction_bank_record)
        iterator = map(_compile_worker, items)
        pool = None
    else:
        context = mp.get_context("spawn" if os.name == "nt" else "fork")
        pool = context.Pool(
            processes=workers,
            initializer=_initialize_worker,
            initargs=(block6_bank_record, block8_bank_record, abstraction_bank_record),
            maxtasksperchild=50,
        )
        iterator = pool.imap_unordered(_compile_worker, items, chunksize=2)
    try:
        for task_id, record in iterator:
            records[task_id] = record
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    return {task_id: records[task_id] for task_id in sorted(challenges)}


def _candidate_outputs(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(
        tuple(tuple(int(cell) for cell in row) for row in grid)
        for grid in candidate["test_outputs"]
    )


def _targets(solutions: Mapping[str, Any], task_id: str) -> tuple[Any, ...]:
    return tuple(
        tuple(tuple(int(cell) for cell in row) for row in grid)
        for grid in solutions[task_id]
    )


def unique_candidate(record: Mapping[str, Any]) -> Mapping[str, Any] | None:
    candidates = tuple(record.get("candidates", ()))
    return candidates[0] if len(candidates) == 1 else None


def apply_unique_behavior_policy(
    baseline: Mapping[str, Any],
    records: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply every unique behavior without consulting held-out labels."""
    submission = copy.deepcopy(baseline)
    ledger: dict[str, Any] = {}
    for task_id in sorted(records):
        record = records[task_id]
        candidate = unique_candidate(record)
        item: dict[str, Any] = {
            "candidate_behaviors": len(record.get("candidates", ())),
            "committed": False,
            "reason": "no_candidate" if not record.get("candidates") else "ambiguous_behaviors",
        }
        if candidate is not None:
            outputs = _candidate_outputs(candidate)
            if task_id not in submission or len(outputs) != len(submission[task_id]):
                item["reason"] = "output_arity_mismatch"
            else:
                for index, grid in enumerate(outputs):
                    submission[task_id][index]["attempt_2"] = [list(row) for row in grid]
                program = candidate["program"]
                item.update({
                    "committed": True,
                    "reason": "unique_behavior",
                    "semantic_hash": program["semantic_hash"],
                    "leaf_families": [leaf["family"] for leaf in program["leaves"]],
                    "leaf_count": int(program["leaf_count"]),
                    "behavior_hash": candidate["behavior_hash"],
                })
        ledger[task_id] = item
    return submission, ledger


def candidate_statistics(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> dict[str, Any]:
    tasks_with_candidates = 0
    unique = exact = wrong = ambiguous = 0
    exact_outputs = wrong_outputs = 0
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    events = []
    for task_id in sorted(records):
        candidates = tuple(records[task_id].get("candidates", ()))
        if candidates:
            tasks_with_candidates += 1
        if len(candidates) > 1:
            ambiguous += 1
            continue
        if not candidates:
            continue
        unique += 1
        candidate = candidates[0]
        outputs = _candidate_outputs(candidate)
        targets = _targets(solutions, task_id)
        task_exact = outputs == targets
        exact += int(task_exact)
        wrong += int(not task_exact)
        output_exactness = tuple(output == target for output, target in zip(outputs, targets))
        exact_outputs += sum(output_exactness)
        wrong_outputs += len(output_exactness) - sum(output_exactness)
        families = tuple(leaf["family"] for leaf in candidate["program"]["leaves"])
        for family in families:
            by_family[family]["activations"] += 1
            by_family[family]["exact"] += int(task_exact)
            by_family[family]["wrong"] += int(not task_exact)
        events.append({
            "task_id": task_id,
            "correct": task_exact,
            "output_exactness": list(output_exactness),
            "leaf_families": list(families),
            "semantic_hash": candidate["program"]["semantic_hash"],
            "behavior_hash": candidate["behavior_hash"],
        })
    return {
        "tasks_with_candidates": tasks_with_candidates,
        "unique_behavior_tasks": unique,
        "ambiguous_behavior_tasks": ambiguous,
        "exact_unique_tasks": exact,
        "wrong_unique_tasks": wrong,
        "exact_candidate_outputs": exact_outputs,
        "wrong_candidate_outputs": wrong_outputs,
        "family_statistics": {
            family: dict(sorted(counts.items())) for family, counts in sorted(by_family.items())
        },
        "events": events,
    }


def build_abstraction_closure(
    challenges: Mapping[str, Any],
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], tuple[Any, ...]]:
    occurrences: list[SubtreeOccurrence] = []
    for task_id in sorted(records):
        candidate = unique_candidate(records[task_id])
        if candidate is None or int(candidate["program"]["leaf_count"]) < 2:
            continue
        correct = _candidate_outputs(candidate) == _targets(solutions, task_id)
        occurrences.extend(extract_contiguous_subtrees(
            candidate["program"],
            training_content={"train": challenges[task_id]["train"]},
            correct=correct,
            audit_id=task_id,
            program_id=candidate["program"]["derivation_hash"],
            minimum_leaves=2,
        ))
    groups: dict[str, list[SubtreeOccurrence]] = defaultdict(list)
    for occurrence in occurrences:
        groups[occurrence.shape_key].append(occurrence)
    evidence = AbstractionEvidenceBank()
    for shape_key in sorted(groups):
        evidence.ingest_occurrences(groups[shape_key])
    runtime = evidence.runtime_bank(stable_only=True)
    return evidence.audit_record(), runtime.to_runtime_record(), evidence.templates()


def prospective_subtree_reuse(
    challenges: Mapping[str, Any],
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    salt: str = "block9-prequential-v1:",
) -> dict[str, Any]:
    """Freeze evidence before each label; report authorization, not score gain."""
    order = sorted(records, key=lambda task_id: hashlib.sha256((salt + task_id).encode()).hexdigest())
    revealed: list[tuple[SubtreeOccurrence, ...]] = []
    active_schemas: set[str] = set()
    eligible = exact = wrong = 0
    events = []
    for position, task_id in enumerate(order, 1):
        candidate = unique_candidate(records[task_id])
        current: tuple[SubtreeOccurrence, ...] = ()
        if candidate is not None and int(candidate["program"]["leaf_count"]) >= 2:
            correct = _candidate_outputs(candidate) == _targets(solutions, task_id)
            current = extract_contiguous_subtrees(
                candidate["program"],
                training_content={"train": challenges[task_id]["train"]},
                correct=correct,
                audit_id=task_id,
                program_id=candidate["program"]["derivation_hash"],
                minimum_leaves=2,
            )
            schemas = {semantic_subtree_schema(item.leaves) for item in current}
            if schemas.intersection(active_schemas):
                eligible += 1
                exact += int(correct)
                wrong += int(not correct)
                events.append({
                    "position": position,
                    "task_id": task_id,
                    "correct": correct,
                    "active_schemas": sorted(schemas.intersection(active_schemas)),
                })
        # Reveal only now, then rebuild support from canonical training content.
        if current:
            revealed.append(current)
        support: dict[str, set[str]] = defaultdict(set)
        failures: set[str] = set()
        for batch in revealed:
            for occurrence in batch:
                if occurrence.correct:
                    support[semantic_subtree_schema(occurrence.leaves)].add(occurrence.training_content_hash)
                else:
                    failures.add(semantic_subtree_schema(occurrence.leaves))
        active_schemas = {
            schema for schema, hashes in support.items()
            if len(hashes) >= 2 and schema not in failures
        }
    return {
        "protocol": "compile_with_frozen_base_grammar_then_authorize_subtree_before_label",
        "order": f"sha256({salt}task_id)",
        "minimum_prior_distinct_content": 2,
        "eligible_predictions": eligible,
        "exact_predictions": exact,
        "wrong_predictions": wrong,
        "events": events,
    }


def shifted_label_control(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> dict[str, Any]:
    ids = sorted(records)
    shifted = {task_id: solutions[ids[(index + 1) % len(ids)]] for index, task_id in enumerate(ids)}
    comparable = accidental = 0
    for task_id in ids:
        candidate = unique_candidate(records[task_id])
        if candidate is None:
            continue
        outputs = _candidate_outputs(candidate)
        try:
            targets = tuple(
                tuple(tuple(int(cell) for cell in row) for row in grid)
                for grid in shifted[task_id]
            )
        except Exception:
            continue
        if len(outputs) != len(targets):
            continue
        comparable += 1
        accidental += int(outputs == targets)
    return {
        "control": "cyclically_shifted_public_labels",
        "comparable_unique_candidates": comparable,
        "accidental_exact_matches": accidental,
    }


def run_audit(
    root: Path,
    *,
    workers: int,
    records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    challenges_path = root / "data/arc-agi_training_challenges.json"
    solutions_path = root / "data/arc-agi_training_solutions.json"
    baseline_path = root / "block8/results/block8_submission.json"
    block6_bank_path = root / "block7/src/komorebi_lasm_grammar/data/runtime_macro_bank.json"
    block8_bank_path = root / "block8/src/komorebi_lasm_synthesis/data/runtime_macro_bank.json"
    challenges = load_json(challenges_path)
    solutions = load_json(solutions_path)
    baseline = load_json(baseline_path)
    block6_bank = load_json(block6_bank_path)
    block8_bank = load_json(block8_bank_path)
    runtime_bank_path = root / "block9/src/komorebi_lasm_composition/data/runtime_abstraction_bank.json"
    runtime_bank_record = load_json(runtime_bank_path)
    if records is None:
        records = compile_corpus(
            challenges,
            block6_bank_record=block6_bank,
            block8_bank_record=block8_bank,
            abstraction_bank_record=runtime_bank_record,
            workers=workers,
        )
    submission, policy_ledger = apply_unique_behavior_policy(baseline, records)
    baseline_score = score_submission(baseline, solutions)
    score = score_submission(submission, solutions)
    statistics = candidate_statistics(records, solutions)
    abstraction_audit, runtime_bank, templates = build_abstraction_closure(
        challenges, records, solutions,
    )
    exact_before = set(baseline_score["exact_keys"])
    exact_after = set(score["exact_keys"])
    new_exact = sorted(exact_after - exact_before)
    lost = sorted(exact_before - exact_after)
    wrong_commits = int(statistics["wrong_candidate_outputs"])
    attempt1_preserved = all(
        baseline[task_id][index]["attempt_1"] == submission[task_id][index]["attempt_1"]
        for task_id in baseline for index in range(len(baseline[task_id]))
    )
    compile_errors = {
        task_id: record["error"] for task_id, record in records.items() if record.get("error")
    }
    result = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "claim_boundary": (
            "Complete retrospective public-training audit. Compilation reads labelled "
            "training demonstrations only; test inputs execute only after exact programs freeze. "
            "This is not an official, private-test, or hidden-test result."
        ),
        "source_hashes": {
            "challenges": hashlib.sha256(challenges_path.read_bytes()).hexdigest(),
            "solutions": hashlib.sha256(solutions_path.read_bytes()).hexdigest(),
            "block8_submission": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
            "block6_runtime_bank": hashlib.sha256(block6_bank_path.read_bytes()).hexdigest(),
            "block8_runtime_bank": hashlib.sha256(block8_bank_path.read_bytes()).hexdigest(),
            "block9_runtime_bank": hashlib.sha256(runtime_bank_path.read_bytes()).hexdigest(),
        },
        "baseline": {key: baseline_score[key] for key in (
            "exact", "total", "rate", "whole_tasks", "task_total",
            "attempt_1_exact", "attempt_2_incremental_exact",
        )},
        "block9": {key: score[key] for key in (
            "exact", "total", "rate", "whole_tasks", "task_total",
            "attempt_1_exact", "attempt_2_incremental_exact",
        )},
        "net_gain": int(score["exact"] - baseline_score["exact"]),
        "whole_task_gain": int(score["whole_tasks"] - baseline_score["whole_tasks"]),
        "new_exact_outputs": new_exact,
        "lost_exact_outputs": lost,
        "wrong_committed_outputs": wrong_commits,
        "attempt_1_preserved": attempt1_preserved,
        "candidate_statistics": statistics,
        "compile_errors": compile_errors,
        "stable_composite_macros": sum(template.status is PromotionStatus.STABLE for template in templates),
        "provisional_composite_macros": sum(template.status is PromotionStatus.PROVISIONAL for template in templates),
        "runtime_abstraction_bank_id": runtime_bank["bank_id"],
        "prequential_subtree_reuse": prospective_subtree_reuse(challenges, records, solutions),
        "shifted_label_control": shifted_label_control(records, solutions),
        "release_gates": {
            "inherited_floor_318": baseline_score["exact"] == 318,
            "inherited_whole_tasks_288": baseline_score["whole_tasks"] == 288,
            "attempt1_byte_values_preserved": attempt1_preserved,
            "no_lost_exact_outputs": not lost,
            "no_wrong_unique_commits": wrong_commits == 0,
            "no_compile_errors": not compile_errors,
            "runtime_bank_stable_only": all(
                macro["status"] == "stable" for macro in runtime_bank["macros"]
            ),
        },
    }
    result["release_pass"] = all(result["release_gates"].values())
    result["content_hash"] = sha256_record(result)
    return {
        "validation": result,
        "records": records,
        "submission": submission,
        "policy_ledger": policy_ledger,
        "abstraction_audit": abstraction_audit,
        "runtime_bank": runtime_bank,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 1)))
    parser.add_argument("--records", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    records = load_json(args.records) if args.records else None
    bundle = run_audit(root, workers=args.workers, records=records)
    output = args.output_dir or (root / "block9/results")
    write_json(output / "composition_records.json", bundle["records"])
    write_json(output / "block9_submission.json", bundle["submission"])
    write_json(output / "unique_behavior_policy_ledger.json", bundle["policy_ledger"])
    write_json(output / "subtree_evidence_audit.json", bundle["abstraction_audit"])
    write_json(output / "runtime_abstraction_bank.json", bundle["runtime_bank"])
    write_json(output / "block9_validation.json", bundle["validation"])
    validation = bundle["validation"]
    print(json.dumps({
        "release_pass": validation["release_pass"],
        "exact": validation["block9"]["exact"],
        "total": validation["block9"]["total"],
        "whole_tasks": validation["block9"]["whole_tasks"],
        "net_gain": validation["net_gain"],
        "new_exact_outputs": validation["new_exact_outputs"],
        "wrong_committed_outputs": validation["wrong_committed_outputs"],
        "lost_exact_outputs": validation["lost_exact_outputs"],
        "compile_errors": len(validation["compile_errors"]),
    }, indent=2, sort_keys=True))
    return 0 if validation["release_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "apply_unique_behavior_policy",
    "build_abstraction_closure",
    "candidate_statistics",
    "compile_corpus",
    "load_json",
    "main",
    "prospective_subtree_reuse",
    "run_audit",
    "shifted_label_control",
    "unique_candidate",
    "write_json",
]
