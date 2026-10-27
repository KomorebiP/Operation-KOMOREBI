"""Complete Persistent Grammar Promotion audit for PR-LASM Block 7."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.audit import score_submission
from komorebi_lasm_compiler.common import equal, freeze
from komorebi_lasm_compiler.model import canonical_value, sha256_record

from .abstraction import abstraction_key, exact_signature_key
from .bank import PersistentEvidenceBank
from .discovery import (
    candidate_correct,
    candidate_family,
    candidate_outputs,
    candidate_parameters,
    candidate_signature,
    expanded_record,
)
from .model import MacroBank, MacroStatus


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(canonical_value(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _semantic_records_hash(records: Mapping[str, Any]) -> str:
    def strip_timing(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(key): strip_timing(item) for key, item in value.items() if str(key) != "elapsed_seconds"}
        if isinstance(value, (list, tuple)):
            return [strip_timing(item) for item in value]
        return value
    return sha256_record(strip_timing(records))


def build_expanded_records(
    challenges: Mapping[str, Any],
    routed_records: Mapping[str, Any],
) -> dict[str, Any]:
    """Add bounded, training-only broad activations to Block 6 records."""
    result = {}
    for task_id in sorted(challenges):
        result[task_id] = expanded_record(
            challenges[task_id],
            routed_records[task_id],
            audit_discovery=True,
        )
    return result


def evidence_from_records(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    task_ids: Iterable[str] | None = None,
    minimum_support: int = 2,
) -> PersistentEvidenceBank:
    bank = PersistentEvidenceBank(minimum_support=minimum_support)
    ids = sorted(records) if task_ids is None else sorted(str(value) for value in task_ids)
    for task_id in ids:
        targets = solutions[task_id]
        for candidate in records[task_id].get("candidates", []):
            bank.observe_candidate(
                task_id=task_id,
                family=candidate_family(candidate),
                parameters=candidate_parameters(candidate),
                signature=candidate_signature(candidate),
                correct=candidate_correct(candidate, targets),
            )
    return bank


def _matching_candidates(record: Mapping[str, Any], bank: MacroBank) -> list[Mapping[str, Any]]:
    return [
        candidate
        for candidate in record.get("candidates", [])
        if bank.permits(candidate_family(candidate), candidate_parameters(candidate))
    ]


def _stable_evidence_keys(evidence: PersistentEvidenceBank) -> set[str]:
    return {
        key
        for key, item in evidence.evidence.items()
        if item.wrong_count == 0 and item.exact_source_tasks >= evidence.minimum_support
    }


def _matching_key_candidates(record: Mapping[str, Any], stable_keys: set[str]) -> list[Mapping[str, Any]]:
    return [
        candidate
        for candidate in record.get("candidates", [])
        if abstraction_key(candidate_family(candidate), candidate_parameters(candidate)) in stable_keys
    ]


def _unique_behavior(candidates: Sequence[Mapping[str, Any]]) -> tuple[Any | None, list[Mapping[str, Any]], int]:
    by_output: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_output[candidate_outputs(candidate)].append(candidate)
    if len(by_output) != 1:
        return None, [], len(by_output)
    output, matching = next(iter(by_output.items()))
    return output, matching, 1


def _order(task_ids: Iterable[str], salt: str) -> list[str]:
    return sorted(
        (str(value) for value in task_ids),
        key=lambda value: hashlib.sha256((salt + value).encode("utf-8")).hexdigest(),
    )


def prequential_transfer(
    routed_records: Mapping[str, Any],
    expanded_records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    salt: str = "komorebi-block7-prequential:",
    minimum_support: int = 2,
    include_events: bool = True,
) -> dict[str, Any]:
    """Prospective within-corpus transfer with predict-before-reveal semantics."""
    evidence = PersistentEvidenceBank(minimum_support=minimum_support)
    eligible = exact = wrong = predicted_outputs = exact_outputs = route_overrides = 0
    events = []
    promotion_events = []
    previous_stable: set[str] = set()

    for position, task_id in enumerate(_order(expanded_records, salt), 1):
        # Compute the admissible abstraction keys before seeing the current label.
        # Building full anti-unified templates at every step would be needless; the
        # template bank is materialized only after the final observation.
        current_stable = _stable_evidence_keys(evidence)
        newly_stable = sorted(current_stable - previous_stable)
        retired = sorted(previous_stable - current_stable)
        if newly_stable or retired:
            promotion_events.append({
                "position": position,
                "promoted_key_hashes": [sha256_record(value) for value in newly_stable],
                "retired_key_hashes": [sha256_record(value) for value in retired],
                "stable_macro_count": len(current_stable),
            })
        previous_stable = current_stable

        candidates = _matching_key_candidates(expanded_records[task_id], current_stable)
        output, matching, behavior_count = _unique_behavior(candidates)
        if output is not None:
            targets = tuple(freeze(value) for value in solutions[task_id])
            correct = output == targets
            output_count = len(output)
            eligible += 1
            exact += int(correct)
            wrong += int(not correct)
            predicted_outputs += output_count
            exact_outputs += output_count if correct else 0
            original_empty = not routed_records[task_id].get("candidates", [])
            broad_selected = any(
                candidate["program"].get("origin") == "persistent_macro_broad_activation"
                for candidate in matching
            )
            is_override = bool(original_empty and broad_selected)
            route_overrides += int(is_override)
            if include_events:
                events.append({
                    "position": position,
                    "task_id": task_id,
                    "correct": correct,
                    "output_count": output_count,
                    "route_override": is_override,
                    "families": sorted({candidate_family(candidate) for candidate in matching}),
                    "signatures": sorted({candidate_signature(candidate) for candidate in matching}),
                    "macro_key_hashes": sorted({
                        sha256_record(abstraction_key(candidate_family(candidate), candidate_parameters(candidate)))
                        for candidate in matching
                    }),
                })

        # Reveal the current label only now and update the persistent evidence.
        targets = solutions[task_id]
        for candidate in expanded_records[task_id].get("candidates", []):
            evidence.observe_candidate(
                task_id=task_id,
                family=candidate_family(candidate),
                parameters=candidate_parameters(candidate),
                signature=candidate_signature(candidate),
                correct=candidate_correct(candidate, targets),
            )

    final_bank = evidence.stable_bank()
    return {
        "schema": "komorebi.lasm_block7_prequential_transfer",
        "schema_version": 1,
        "order": f"sha256({salt}task_id)",
        "minimum_prior_exact_tasks": minimum_support,
        "eligible_predictions": eligible,
        "exact_predictions": exact,
        "wrong_predictions": wrong,
        "accuracy": exact / eligible if eligible else 0.0,
        "predicted_outputs": predicted_outputs,
        "exact_predicted_outputs": exact_outputs,
        "route_override_predictions": route_overrides,
        "final_stable_macro_count": len(final_bank.macros),
        "final_bank_id": final_bank.bank_id,
        "promotion_events": promotion_events if include_events else [],
        "events": events if include_events else [],
    }

def exact_signature_prequential(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    salt: str = "komorebi-block7-prequential:",
) -> dict[str, Any]:
    history: dict[str, Counter] = defaultdict(Counter)
    eligible = exact = wrong = 0
    events = []
    for position, task_id in enumerate(_order(records, salt), 1):
        candidates = []
        for candidate in records[task_id].get("candidates", []):
            state = history[candidate_signature(candidate)]
            if state["exact"] >= 1 and state["wrong"] == 0:
                candidates.append(candidate)
        output, matching, _ = _unique_behavior(candidates)
        if output is not None:
            correct = output == tuple(freeze(value) for value in solutions[task_id])
            eligible += 1; exact += int(correct); wrong += int(not correct)
            events.append({
                "position": position,
                "task_id": task_id,
                "correct": correct,
                "signatures": sorted({candidate_signature(candidate) for candidate in matching}),
            })
        for candidate in records[task_id].get("candidates", []):
            correct = candidate_correct(candidate, solutions[task_id])
            state = history[candidate_signature(candidate)]
            state["exact"] += int(correct)
            state["wrong"] += int(not correct)
    return {
        "scope": "exact_signature",
        "minimum_prior_exact": 1,
        "eligible_predictions": eligible,
        "exact_predictions": exact,
        "wrong_predictions": wrong,
        "accuracy": exact / eligible if eligible else 0.0,
        "events": events,
    }


def fold_transfer(
    routed_records: Mapping[str, Any],
    expanded_records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    salt: str,
    modulo: int = 5,
) -> dict[str, Any]:
    folds = []
    total_eligible = total_exact = total_wrong = total_outputs = total_override = 0
    task_ids = sorted(expanded_records)
    for holdout_bucket in range(modulo):
        train_ids = []
        holdout_ids = []
        for task_id in task_ids:
            bucket = int(hashlib.sha256((salt + task_id).encode("utf-8")).hexdigest(), 16) % modulo
            (holdout_ids if bucket == holdout_bucket else train_ids).append(task_id)
        evidence = evidence_from_records(expanded_records, solutions, task_ids=train_ids)
        stable_keys = _stable_evidence_keys(evidence)
        eligible = exact = wrong = outputs = override = 0
        events = []
        for task_id in holdout_ids:
            candidates = _matching_key_candidates(expanded_records[task_id], stable_keys)
            output, matching, _ = _unique_behavior(candidates)
            if output is None:
                continue
            correct = output == tuple(freeze(value) for value in solutions[task_id])
            is_override = bool(
                not routed_records[task_id].get("candidates", [])
                and any(candidate["program"].get("origin") == "persistent_macro_broad_activation" for candidate in matching)
            )
            eligible += 1; exact += int(correct); wrong += int(not correct)
            outputs += len(output); override += int(is_override)
            events.append({
                "task_id": task_id,
                "correct": correct,
                "route_override": is_override,
                "families": sorted({candidate_family(candidate) for candidate in matching}),
            })
        fold = {
            "holdout_bucket": holdout_bucket,
            "train_tasks": len(train_ids),
            "holdout_tasks": len(holdout_ids),
            "stable_macros": len(stable_keys),
            "eligible_predictions": eligible,
            "exact_predictions": exact,
            "wrong_predictions": wrong,
            "predicted_outputs": outputs,
            "route_override_predictions": override,
            "accuracy": exact / eligible if eligible else 0.0,
            "events": events,
        }
        folds.append(fold)
        total_eligible += eligible; total_exact += exact; total_wrong += wrong
        total_outputs += outputs; total_override += override
    return {
        "split": f"complete {modulo}-fold SHA-256 task partition using salt {salt!r}",
        "eligible_predictions": total_eligible,
        "exact_predictions": total_exact,
        "wrong_predictions": total_wrong,
        "predicted_outputs": total_outputs,
        "route_override_predictions": total_override,
        "accuracy": total_exact / total_eligible if total_eligible else 0.0,
        "folds": folds,
    }


def order_robustness(
    routed_records: Mapping[str, Any],
    expanded_records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    trials: int = 64,
) -> dict[str, Any]:
    runs = []
    for index in range(trials):
        value = prequential_transfer(
            routed_records,
            expanded_records,
            solutions,
            salt=f"komorebi-block7-order-{index}:",
            include_events=False,
        )
        runs.append({
            "trial": index,
            "eligible_predictions": value["eligible_predictions"],
            "exact_predictions": value["exact_predictions"],
            "wrong_predictions": value["wrong_predictions"],
            "route_override_predictions": value["route_override_predictions"],
        })
    return {
        "trials": trials,
        "eligible_predictions": sum(item["eligible_predictions"] for item in runs),
        "exact_predictions": sum(item["exact_predictions"] for item in runs),
        "wrong_predictions": sum(item["wrong_predictions"] for item in runs),
        "route_override_predictions": sum(item["route_override_predictions"] for item in runs),
        "minimum_eligible_per_trial": min((item["eligible_predictions"] for item in runs), default=0),
        "maximum_eligible_per_trial": max((item["eligible_predictions"] for item in runs), default=0),
        "runs": runs,
    }


def partition_robustness(
    routed_records: Mapping[str, Any],
    expanded_records: Mapping[str, Any],
    solutions: Mapping[str, Any],
    *,
    trials: int = 32,
) -> dict[str, Any]:
    runs = []
    for index in range(trials):
        value = fold_transfer(
            routed_records,
            expanded_records,
            solutions,
            salt=f"komorebi-block7-fold-{index}:",
        )
        runs.append({
            "trial": index,
            "eligible_predictions": value["eligible_predictions"],
            "exact_predictions": value["exact_predictions"],
            "wrong_predictions": value["wrong_predictions"],
            "route_override_predictions": value["route_override_predictions"],
        })
    return {
        "trials": trials,
        "folds_evaluated": 5 * trials,
        "eligible_predictions": sum(item["eligible_predictions"] for item in runs),
        "exact_predictions": sum(item["exact_predictions"] for item in runs),
        "wrong_predictions": sum(item["wrong_predictions"] for item in runs),
        "route_override_predictions": sum(item["route_override_predictions"] for item in runs),
        "minimum_eligible_per_partition": min((item["eligible_predictions"] for item in runs), default=0),
        "maximum_eligible_per_partition": max((item["eligible_predictions"] for item in runs), default=0),
        "runs": runs,
    }


def apply_route_overrides(
    baseline_submission: Mapping[str, Any],
    routed_records: Mapping[str, Any],
    expanded_records: Mapping[str, Any],
    bank: MacroBank,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply only unique macro behaviors to tasks with no Block 6 candidate."""
    submission = copy.deepcopy(baseline_submission)
    ledger = {}
    for task_id in sorted(expanded_records):
        item = {
            "committed": False,
            "reason": "routed_candidates_present" if routed_records[task_id].get("candidates", []) else "no_macro_candidate",
        }
        if routed_records[task_id].get("candidates", []):
            ledger[task_id] = item
            continue
        candidates = _matching_candidates(expanded_records[task_id], bank)
        # A route override must come from the explicit broad-activation path.
        candidates = [
            candidate for candidate in candidates
            if candidate["program"].get("origin") == "persistent_macro_broad_activation"
        ]
        output, matching, behavior_count = _unique_behavior(candidates)
        if output is None:
            item["reason"] = "ambiguous_macro_behaviors" if behavior_count > 1 else "no_macro_candidate"
            item["behavior_count"] = behavior_count
            ledger[task_id] = item
            continue
        if len(output) != len(submission[task_id]):
            item["reason"] = "test_output_count_mismatch"
            ledger[task_id] = item
            continue
        for index, grid in enumerate(output):
            submission[task_id][index]["attempt_2"] = [list(row) for row in grid]
        item.update({
            "committed": True,
            "reason": "unique_stable_macro_behavior",
            "families": sorted({candidate_family(candidate) for candidate in matching}),
            "signatures": sorted({candidate_signature(candidate) for candidate in matching}),
            "macro_ids": sorted({
                macro.macro_id
                for candidate in matching
                for macro in bank.matching(candidate_family(candidate), candidate_parameters(candidate))
            }),
            "output_hash": sha256_record(output),
            "equivalent_programs": len(matching),
        })
        ledger[task_id] = item
    return submission, ledger


def shuffled_label_control(
    records: Mapping[str, Any],
    solutions: Mapping[str, Any],
) -> dict[str, Any]:
    """Negative control: update evidence with deterministically mismatched labels."""
    ids = sorted(records)
    shifted = ids[1:] + ids[:1]
    evidence = PersistentEvidenceBank(minimum_support=2)
    compared = compatible = 0
    for task_id, wrong_id in zip(ids, shifted):
        wrong_targets = solutions[wrong_id]
        for candidate in records[task_id].get("candidates", []):
            compared += 1
            correct = candidate_outputs(candidate) == tuple(freeze(value) for value in wrong_targets)
            compatible += int(correct)
            evidence.observe_candidate(
                task_id=task_id,
                family=candidate_family(candidate),
                parameters=candidate_parameters(candidate),
                signature=candidate_signature(candidate),
                correct=correct,
            )
    bank = evidence.stable_bank()
    return {
        "control": "cyclically shifted task labels",
        "candidate_label_comparisons": compared,
        "accidental_exact_comparisons": compatible,
        "stable_macro_count": len(bank.macros),
        "bank_id": bank.bank_id,
    }


def _exact_evidence_digest(records: Mapping[str, Any], solutions: Mapping[str, Any]) -> str:
    rows = []
    for task_id in sorted(records):
        truth = tuple(freeze(value) for value in solutions[task_id])
        for candidate in records[task_id].get("candidates", []):
            rows.append({
                "task_id": task_id,
                "signature": candidate_signature(candidate),
                "correct": candidate_outputs(candidate) == truth,
            })
    return sha256_record(rows)


def audit(
    challenges: Mapping[str, Any],
    solutions: Mapping[str, Any],
    block6_submission: Mapping[str, Any],
    routed_records: Mapping[str, Any],
    *,
    order_trials: int = 64,
    partition_trials: int = 32,
) -> dict[str, Any]:
    started = time.perf_counter()
    expanded = build_expanded_records(challenges, routed_records)
    full_evidence = evidence_from_records(expanded, solutions)
    runtime_bank = full_evidence.stable_bank()
    submission, override_ledger = apply_route_overrides(block6_submission, routed_records, expanded, runtime_bank)
    baseline_score = score_submission(block6_submission, solutions)
    block7_score = score_submission(submission, solutions)
    baseline_keys = set(baseline_score["exact_keys"])
    block7_keys = set(block7_score["exact_keys"])

    wrong_commits = []
    exact_commits = []
    for task_id, item in override_ledger.items():
        if not item.get("committed"):
            continue
        for index, target in enumerate(solutions[task_id]):
            key = f"{task_id}:{index}"
            if equal(submission[task_id][index]["attempt_2"], target):
                exact_commits.append(key)
            else:
                wrong_commits.append(key)

    prequential = prequential_transfer(routed_records, expanded, solutions)
    exact_signature = exact_signature_prequential(expanded, solutions)
    primary_five_fold = fold_transfer(
        routed_records,
        expanded,
        solutions,
        salt="komorebi-block7-fivefold:",
    )
    order_checks = order_robustness(
        routed_records,
        expanded,
        solutions,
        trials=order_trials,
    )
    partition_checks = partition_robustness(
        routed_records,
        expanded,
        solutions,
        trials=partition_trials,
    )
    shuffled = shuffled_label_control(expanded, solutions)

    macro_audit = full_evidence.audit_record()
    runtime_record = runtime_bank.to_runtime_record()
    stable_families = Counter(macro.family for macro in runtime_bank.macros)
    promoted = [macro.to_record() for macro in runtime_bank.macros]
    runtime_exact_ids = []
    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for item in value.values(): visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
        elif isinstance(value, str) and re.fullmatch(r"[0-9a-f]{8}", value):
            runtime_exact_ids.append(value)
    visit(runtime_record)

    validation = {
        "schema": "komorebi.lasm_block7_validation",
        "schema_version": 1,
        "block": "Persistent Grammar Promotion",
        "baseline": {key: value for key, value in baseline_score.items() if key not in {"exact_keys", "per_task"}},
        "block7": {key: value for key, value in block7_score.items() if key not in {"exact_keys", "per_task"}},
        "net_gain": block7_score["exact"] - baseline_score["exact"],
        "whole_task_gain": block7_score["whole_tasks"] - baseline_score["whole_tasks"],
        "new_exact_outputs": sorted(block7_keys - baseline_keys),
        "lost_exact_outputs": sorted(baseline_keys - block7_keys),
        "route_override_tasks": sorted(task_id for task_id, item in override_ledger.items() if item.get("committed")),
        "exact_route_override_outputs": sorted(exact_commits),
        "wrong_committed_outputs": sorted(wrong_commits),
        "routed_candidate_count": sum(len(record.get("candidates", [])) for record in routed_records.values()),
        "expanded_candidate_count": sum(len(record.get("candidates", [])) for record in expanded.values()),
        "tasks_with_added_candidates": sum(
            len(expanded[task_id].get("candidates", [])) > len(routed_records[task_id].get("candidates", []))
            for task_id in expanded
        ),
        "stable_macro_count": len(runtime_bank.macros),
        "stable_macro_families": dict(sorted(stable_families.items())),
        "runtime_bank_id": runtime_bank.bank_id,
        "runtime_task_id_literals": sorted(runtime_exact_ids),
        "macro_compression": {
            "raw_bytes": sum(macro.compression.raw_bytes for macro in runtime_bank.macros),
            "macro_bytes": sum(macro.compression.macro_bytes for macro in runtime_bank.macros),
            "instantiation_bytes": sum(macro.compression.instantiation_bytes for macro in runtime_bank.macros),
            "compression_gain_bytes": sum(macro.compression.compression_gain_bytes for macro in runtime_bank.macros),
            "positive_gain_macros": sum(macro.compression.compression_gain_bytes > 0 for macro in runtime_bank.macros),
        },
        "prequential_transfer": prequential,
        "exact_signature_baseline": exact_signature,
        "five_fold_transfer": primary_five_fold,
        "order_robustness": order_checks,
        "partition_robustness": partition_checks,
        "shuffled_label_control": shuffled,
        "reproducibility": {
            "routed_records_sha256": _semantic_records_hash(routed_records),
            "expanded_records_sha256": _semantic_records_hash(expanded),
            "macro_evidence_sha256": sha256_record(macro_audit),
            "runtime_macro_bank_sha256": sha256_record(runtime_record),
            "submission_sha256": sha256_record(submission),
            "override_ledger_sha256": sha256_record(override_ledger),
            "candidate_correctness_ledger_sha256": _exact_evidence_digest(expanded, solutions),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "release_gates": {
            "baseline_floor_305": baseline_score["exact"] == 305 and baseline_score["total"] == 1076,
            "baseline_whole_275": baseline_score["whole_tasks"] == 275,
            "block7_floor_306": block7_score["exact"] >= 306,
            "block7_whole_276": block7_score["whole_tasks"] >= 276,
            "nonregression": baseline_keys <= block7_keys,
            "zero_lost_exact": not (baseline_keys - block7_keys),
            "zero_wrong_commits": not wrong_commits,
            "minimum_eight_stable_macros": len(runtime_bank.macros) >= 8,
            "runtime_bank_task_id_free": not runtime_exact_ids,
            "prequential_minimum_thirty": prequential["exact_predictions"] >= 30,
            "prequential_zero_wrong": prequential["wrong_predictions"] == 0,
            "prequential_beats_exact_signature": prequential["exact_predictions"] > exact_signature["exact_predictions"],
            "five_fold_minimum_thirty_five": primary_five_fold["exact_predictions"] >= 35,
            "five_fold_zero_wrong": primary_five_fold["wrong_predictions"] == 0,
            "order_robustness_zero_wrong": order_checks["wrong_predictions"] == 0,
            "partition_robustness_zero_wrong": partition_checks["wrong_predictions"] == 0,
            "valid_cardinality": block7_score["total"] == 1076 and block7_score["task_total"] == 1000,
        },
        "claim_boundary": {
            "established": [
                "retrospective complete public-training portfolio score",
                "predict-before-label prequential transfer inside deterministic public-training orders",
                "task-held-out crossfold transfer inside public training",
                "task-ID-free runtime macro bank",
                "zero-regression route override on the declared corpus",
            ],
            "not_established": [
                "official ARC evaluation score",
                "private or hidden-test performance",
                "universal validity of every promoted family",
                "cross-domain grammar transfer",
                "asymptotic optimality of the promotion policy",
            ],
        },
    }
    validation["release_pass"] = all(validation["release_gates"].values())
    return {
        "expanded_records": expanded,
        "macro_audit": macro_audit,
        "runtime_macro_bank": runtime_record,
        "promoted_macros": promoted,
        "submission": submission,
        "override_ledger": override_ledger,
        "validation": validation,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit PR-LASM Persistent Grammar Promotion Block 7")
    parser.add_argument("--challenges", type=Path, required=True)
    parser.add_argument("--solutions", type=Path, required=True)
    parser.add_argument("--block6-submission", type=Path, required=True)
    parser.add_argument("--block6-records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--order-trials", type=int, default=64)
    parser.add_argument("--partition-trials", type=int, default=32)
    args = parser.parse_args(argv)
    result = audit(
        load_json(args.challenges),
        load_json(args.solutions),
        load_json(args.block6_submission),
        load_json(args.block6_records),
        order_trials=args.order_trials,
        partition_trials=args.partition_trials,
    )
    output = args.output
    write_json(output / "expanded_compilation_records.json", result["expanded_records"])
    write_json(output / "macro_evidence_ledger.json", result["macro_audit"])
    write_json(output / "runtime_macro_bank.json", result["runtime_macro_bank"])
    write_json(output / "promoted_macros.json", {"macros": result["promoted_macros"]})
    write_json(output / "block7_submission.json", result["submission"])
    write_json(output / "route_override_ledger.json", result["override_ledger"])
    write_json(output / "prequential_transfer.json", result["validation"]["prequential_transfer"])
    write_json(output / "five_fold_transfer.json", result["validation"]["five_fold_transfer"])
    write_json(output / "order_robustness.json", result["validation"]["order_robustness"])
    write_json(output / "partition_robustness.json", result["validation"]["partition_robustness"])
    write_json(output / "block7_validation.json", result["validation"])
    print(json.dumps(result["validation"], indent=2, sort_keys=True))
    return 0 if result["validation"]["release_pass"] else 2


__all__ = [
    "apply_route_overrides",
    "audit",
    "build_expanded_records",
    "evidence_from_records",
    "exact_signature_prequential",
    "fold_transfer",
    "order_robustness",
    "partition_robustness",
    "prequential_transfer",
]


if __name__ == "__main__":
    raise SystemExit(main())
