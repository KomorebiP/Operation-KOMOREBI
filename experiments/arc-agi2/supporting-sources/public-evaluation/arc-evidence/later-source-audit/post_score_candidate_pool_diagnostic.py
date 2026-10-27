"""Post-score, label-aware candidate coverage diagnostic; never a solver score.

No compilers, candidate programs, dispatcher or ranking functions are called.
The complete census is authenticated in a label-free streaming pass before any
target file is opened. A second pass compares recorded predictions with targets
only after the sealed final scoring receipts and pre-score freeze are verified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

# Standalone execution must never create caches in the frozen source tree.
sys.dont_write_bytecode = True

POLICIES = ("typed_recent", "typed_supported")
PARSER_SHA256 = "3c7811352a40328cff2e1c56db0cbc4f889759e31dd6b455edc6fb2fbbec8d56"
SOURCE_SNAPSHOT_SHA256 = "e655bcf293478ed4da1ce51f903095b0121e285893ecb3e95a49e8749bf47ec8"
CHALLENGE_HASH = "f20b99ee5c2dfbc267e117f2d21f07f3bd599e590152f59b256d3a934c158de8"
RUN_HASH = "d5858775adc7c61a3593c6d058808ecefc97a85a696032213e7810b18cd0751e"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def verify_seal(value):
    require(value.get("content_hash") == digest({k: v for k, v in value.items()
                                               if k != "content_hash"}), "invalid content seal")


def identity(path):
    path = Path(path)
    return {"sha256": sha256(path), "bytes": path.stat().st_size}


def bind(path, expected, bound):
    actual = identity(path)
    require(actual["sha256"] == expected["sha256"], f"file hash mismatch: {path.name}")
    if "bytes" in expected:
        require(actual["bytes"] == expected["bytes"], f"file size mismatch: {path.name}")
    bound[Path(path)] = actual
    return actual


def source_check(root, snapshot):
    actual = {str(p.relative_to(root)): p for p in root.rglob("*") if p.is_file()}
    require(set(actual) == set(snapshot) and len(actual) == 388, "source inventory changed")
    for name, path in actual.items():
        require(path.stat().st_size == snapshot[name]["size"] and
                sha256(path) == snapshot[name]["sha256"], f"source changed: {name}")
    return {name: path.stat().st_mtime_ns for name, path in actual.items()}


def streamed_records(engine, adapter, challenges, census, expected, receipt):
    """Yield one sealed record; publish authentication only after full exhaustion."""
    h = hashlib.sha256(b"{")
    metadata, seen = {}, set()
    first_top, previous_top = True, None
    stream = adapter.JSONStream(census)
    try:
        stream.expect("{")
        while stream.peek() != "}":
            key = stream.value()
            require(isinstance(key, str) and (previous_top is None or key > previous_top),
                    "census keys are not unique and sorted")
            previous_top = key
            stream.expect(":")
            if key != "content_hash":
                if not first_top:
                    h.update(b",")
                h.update(canonical(key) + b":")
                first_top = False
            if key == "records":
                for name in ("bank_hash", "code_hash", "challenges_hash", "limits",
                             "label_access", "champion_fallback"):
                    require(metadata.get(name) == expected[name], f"census {name} binding mismatch")
                stream.expect("{")
                h.update(b"{")
                previous_task, first_record = None, True
                while stream.peek() != "}":
                    task_id = stream.value()
                    require(isinstance(task_id, str) and
                            (previous_task is None or task_id > previous_task),
                            "record keys are not unique and sorted")
                    previous_task = task_id
                    require(task_id in challenges, "unknown census task")
                    stream.expect(":")
                    record = stream.value()
                    engine.verify(record)
                    require(record["task_semantic_hash"] == digest(challenges[task_id]),
                            "record input binding mismatch")
                    adapter.validate_test_membership(engine, task_id, challenges[task_id], record)
                    require(set(record["receipts"]) == expected["providers"],
                            "incomplete compiler-interface receipt membership")
                    for candidate in record["candidates"]:
                        if "train_outputs" in candidate:
                            require(candidate["train_outputs"] ==
                                    [row["output"] for row in challenges[task_id]["train"]],
                                    "candidate demonstration binding mismatch")
                    candidate = None
                    if not first_record:
                        h.update(b",")
                    h.update(canonical(task_id) + b":" + canonical(record))
                    first_record = False
                    seen.add(task_id)
                    yield task_id, record
                    del record
                    delimiter = stream.peek()
                    if delimiter == ",":
                        stream.expect(",")
                    else:
                        require(delimiter == "}", "invalid record delimiter")
                stream.expect("}")
                h.update(b"}")
            else:
                value = stream.value()
                metadata[key] = value
                if key != "content_hash":
                    h.update(canonical(value))
            delimiter = stream.peek()
            if delimiter == ",":
                stream.expect(",")
            else:
                require(delimiter == "}", "invalid census delimiter")
        stream.expect("}")
        require(not stream.peek(), "trailing census data")
        h.update(b"}")
        require(h.hexdigest() == metadata.get("content_hash") == expected["content_hash"],
                "complete semantic census seal mismatch")
        for name in ("schema", "scope", "run_hash", "limits"):
            require(metadata.get(name) == expected[name], f"census {name} mismatch")
        require(seen == set(challenges) and len(seen) == 120, "incomplete census membership")
        require(stream.bytes_digest.hexdigest() == expected["file"]["sha256"] and
                stream.bytes_read == expected["file"]["bytes"], "streamed census bytes changed")
        receipt.update({"complete": True, "records": len(seen), "census_hash": h.hexdigest(),
                        "raw_sha256": stream.bytes_digest.hexdigest(), "raw_bytes": stream.bytes_read})
    finally:
        stream.close()


def metric(rows, tasks, output_key, task_key):
    return {"exact_outputs": sum(row[output_key] for row in rows), "total_outputs": 172,
            "whole_tasks": sum(row[task_key] for row in tasks), "total_tasks": 120}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    root = workspace / "arc-fullbank/block17"
    evidence = workspace / "arc-evidence"
    run = evidence / "fullbank-public-evaluation"
    output = (args.output or run / "post_score_candidate_pool_diagnostic.json").resolve()
    ledger_path = (args.ledger or run / "post_score_candidate_pool_diagnostic.csv").resolve()
    require(output != ledger_path and not output.exists() and not ledger_path.exists(),
            "diagnostic outputs must be new, distinct files")
    require(not output.is_relative_to(root) and not ledger_path.is_relative_to(root),
            "diagnostic outputs must remain outside frozen source")
    freeze_path = run / "predictions_before_scoring.json"
    audit_path = run / "independent_scoring_audit.json"
    census_path = run / "census.json"
    challenges_path = workspace / "arc-offline-data/arc-agi_evaluation_challenges.json"
    solutions_path = workspace / "arc-offline-data/arc-agi_evaluation_solutions.json"
    snapshot_path = evidence / "later-source-audit/block17_source_before.json"
    adapter_path = evidence / "later-source-audit/stream_fresh_block17_dispatch.py"
    require(all(p.is_file() for p in (freeze_path, audit_path, census_path, challenges_path,
                                    snapshot_path, adapter_path)), "final authenticated artifacts are missing")
    require(sha256(snapshot_path) == SOURCE_SNAPSHOT_SHA256, "source snapshot hash changed")
    require(sha256(adapter_path) == PARSER_SHA256, "reviewed stream adapter hash changed")
    snapshot = read(snapshot_path)
    source_mtimes_before = source_check(root, snapshot)
    bound = {snapshot_path: identity(snapshot_path), adapter_path: identity(adapter_path)}
    freeze, audit = read(freeze_path), read(audit_path)
    verify_seal(freeze)
    verify_seal(audit)
    require(freeze.get("schema") == "komorebi.block17.public-evaluation-pre-score-freeze.v1" and
            audit.get("schema") == "komorebi.block17.fresh-public-evaluation-independent-audit.v1",
            "unexpected final artifact schema")
    for record in (freeze, audit):
        require(record.get("tasks") == 120 and record.get("test_outputs") == 172 and
                record.get("primary_policy") == POLICIES[0] and
                record.get("secondary_control_policy") == POLICIES[1], "unexpected freeze protocol")
    require(freeze.get("targets_opened") is False and freeze.get("both_predictions_authenticated") is True and
            freeze.get("policy_sequence") == list(POLICIES) and set(freeze["policies"]) == set(POLICIES),
            "invalid pre-score prediction freeze")
    require(audit.get("integrity_pass") is True and audit.get("membership_complete") is True and
            audit.get("both_predictions_saved_and_authenticated_before_labels") is True and
            audit.get("frozen_source_files_unchanged") is True and
            audit.get("policies_unchanged_before_scoring") is True and
            audit.get("no_champion_fallback") is True and
            audit.get("score_and_ledgers_rechecked_with_direct_grid_comparison") is True,
            "final score integrity assertions did not pass")
    require(freeze["source_unchanged"].get("unchanged") is True and
            audit["source_snapshot_verification"] == freeze["source_unchanged"], "source freeze mismatch")
    require(datetime.fromisoformat(audit["targets_first_scoring_started_utc"]) >=
            datetime.fromisoformat(freeze["frozen_at_utc"]), "scoring preceded prediction freeze")
    bind(freeze_path, audit["pre_score_freeze"], bound)
    require(audit["pre_score_freeze"]["content_hash"] == freeze["content_hash"], "freeze seal mismatch")
    bound[audit_path] = identity(audit_path)
    for path, name in ((census_path, "census"), (challenges_path, "challenges")):
        bind(path, freeze["inputs"][name], bound)
        bind(path, audit[name], bound)
    challenges = read(challenges_path)
    require(all("output" not in row for task in challenges.values() for row in task["test"]),
            "attached query targets rejected")

    spec = importlib.util.spec_from_file_location("reviewed_fresh_stream_adapter", adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    sys.path.insert(0, str(root))
    import engine
    import solver
    require(Path(engine.__file__).resolve() == root / "engine.py" and
            Path(solver.__file__).resolve() == root / "solver.py", "unexpected runtime module origin")
    challenges = {k: engine.sanitize(task) for k, task in challenges.items()}
    require(len(challenges) == 120 and sum(len(t["test"]) for t in challenges.values()) == 172 and
            digest(challenges) == CHALLENGE_HASH, "wrong complete evaluation challenges")
    bindings = {"code_hash": engine.code_hash(), "bank_hash": engine.bank_hash(),
                "prediction_hash": solver.prediction_hash()}
    require(bindings == audit["source_bindings"], "current source does not match final freeze")
    providers = {"core_blocks2_4", *(f"legacy_block{i}" for i in range(6, 13))}
    providers.update(engine.read(root / "bank13.json"))
    providers.update(engine.read(root / "bank14_15.json"))
    require(len(providers) == 77, "unexpected compiler interface inventory")
    expected = {"file": bound[census_path], "content_hash": audit["census"]["content_hash"],
                "schema": "komorebi.block17.live_census.v1", "scope": "all_banks",
                "bank_hash": bindings["bank_hash"], "code_hash": bindings["code_hash"],
                "challenges_hash": CHALLENGE_HASH, "limits": engine.LIMITS,
                "label_access": "demonstrations_only", "champion_fallback": False,
                "run_hash": RUN_HASH, "providers": providers}
    require(digest({"code": bindings["code_hash"], "bank": bindings["bank_hash"],
                    "challenges": challenges, "include_new": True, "limits": engine.LIMITS}) ==
            RUN_HASH == audit["census"]["run_hash"], "full fresh run binding mismatch")
    dispatches, scores = {}, {}
    for policy in POLICIES:
        fixed = freeze["policies"][policy]
        final = audit["policy_results"][policy]
        dispatch_path = run / (policy + "_dispatch.json")
        submission_path = run / (policy + "_submission.json")
        score_path = run / (policy + "_score.json")
        ledger = run / (policy + "_ledger.csv")
        bind(dispatch_path, {"sha256": fixed["dispatch_sha256"]}, bound)
        bind(submission_path, {"sha256": fixed["submission_sha256"]}, bound)
        for path, name in ((dispatch_path, "dispatch"), (submission_path, "submission"),
                           (score_path, "score"), (ledger, "ledger")):
            bind(path, final[name], bound)
        dispatch, submission, score = read(dispatch_path), read(submission_path), read(score_path)
        verify_seal(dispatch)
        require(dispatch["content_hash"] == fixed["dispatch_content_hash"] == final["dispatch_content_hash"] and
                dispatch["policy"] == policy and dispatch["label_access"] == "demonstrations_only" and
                dispatch["champion_fallback"] is False, "frozen dispatch identity mismatch")
        require(dispatch["submission"] == submission and digest(submission) == fixed["submission_hash"] ==
                final["submission_hash"], "frozen submission mismatch")
        require(dispatch["prediction_hash"] == fixed["prediction_hash"] == bindings["prediction_hash"] and
                dispatch["bank_hash"] == fixed["bank_hash"] == bindings["bank_hash"] and
                dispatch["census_hash"] == fixed["census_hash"] == expected["content_hash"],
                "dispatch source or census binding mismatch")
        require(set(submission) == set(dispatch["decisions"]) == set(challenges) and
                all(len(submission[k]) == len(challenges[k]["test"]) for k in challenges),
                "incomplete frozen prediction membership")
        require(score.get("schema") == "komorebi.arc.independent-offline-score.v1" and
                score.get("dataset_split") == "evaluation" and score.get("submission_valid") is True and
                score.get("tasks") == 120 and score.get("test_outputs") == 172 and
                score.get("solver_calls_in_scorer") == 0 and
                score.get("submission_hashed_before_labels_opened") is True and
                datetime.fromisoformat(score["generated_at_utc"]) >=
                datetime.fromisoformat(freeze["frozen_at_utc"]), "final score prerequisites failed")
        require(score["inputs"]["submission"]["sha256"] == fixed["submission_sha256"] and
                score["inputs"]["challenges"]["sha256"] == bound[challenges_path]["sha256"] and
                score["inputs"]["solutions"]["sha256"] == audit["solutions_after_prediction_freeze"]["sha256"] and
                score["per_test_ledger"]["sha256"] == bound[ledger]["sha256"], "final score file bindings differ")
        dispatches[policy], scores[policy] = dispatch, score

    # This entire first streaming pass is label-free. Existing final scores do
    # not substitute for re-authenticating the full census supplied here.
    generated_by_provider, errors_by_provider = Counter(), defaultdict(Counter)
    non_ok_receipts, first_receipt = [], {}
    generated_total = 0
    for task_id, record in streamed_records(engine, adapter, challenges, census_path, expected, first_receipt):
        generated_total += len(record["candidates"])
        generated_by_provider.update(c["entrant"] for c in record["candidates"])
        for provider, item in record["receipts"].items():
            if item.get("status") != "ok":
                errors_by_provider[provider][item.get("status", "missing_status")] += 1
                non_ok_receipts.append({"task_id": task_id, "provider": provider, **item})
        del record
    require(first_receipt.get("complete") is True and generated_total == audit["fresh_candidates"] and
            len(non_ok_receipts) == audit["retained_compiler_error_receipts"], "complete compiler receipt totals differ")
    for path, original in bound.items():
        require(identity(path) == original, f"authenticated input changed: {path.name}")
    require(source_check(root, snapshot) == source_mtimes_before, "source mtime changed before diagnostic target access")

    # FIRST TARGET ACCESS: all freeze, final-score, source, input, prediction and
    # complete census prerequisites have passed. This is a label-aware audit.
    target_bytes = solutions_path.read_bytes()
    target_identity = {"sha256": hashlib.sha256(target_bytes).hexdigest(), "bytes": len(target_bytes)}
    require(target_identity["sha256"] == audit["solutions_after_prediction_freeze"]["sha256"] and
            target_identity["bytes"] == audit["solutions_after_prediction_freeze"]["bytes"],
            "post-score diagnostic target hash mismatch")
    targets = json.loads(target_bytes.decode("utf-8"), object_pairs_hook=no_duplicates)
    del target_bytes
    require(set(targets) == set(challenges) and
            all(len(targets[k]) == len(challenges[k]["test"]) for k in challenges), "target membership differs")
    for grids in targets.values():
        for grid in grids:
            engine.contract.validate_grid(grid, what="diagnostic target")

    rows, task_rows, second_receipt = [], [], {}
    for task_id, record in streamed_records(engine, adapter, challenges, census_path, expected, second_receipt):
        truths = targets[task_id]
        candidates = record["candidates"]
        behavior_hashes = {c["behavior_hash"] for c in candidates}
        eligible = {}
        for policy in POLICIES:
            decision = dispatches[policy]["decisions"][task_id]
            eligible[policy] = {b["behavior_hash"]: b["test_outputs"] for b in decision["behaviors"]}
            require(set(eligible[policy]) <= behavior_hashes, "frozen eligible behavior is outside raw pool")
            for behavior_hash, outputs in eligible[policy].items():
                require(len(outputs) == len(truths) and digest(outputs) == behavior_hash,
                        "frozen eligible behavior binding mismatch")
            require(len(decision["selected_sources"]) == len(truths), "selected source arity mismatch")
        local_rows = []
        for index, truth in enumerate(truths):
            raw_exact = any(c["test_outputs"][index] == truth for c in candidates)
            base = record["base"][index]
            row = {"task_id": task_id, "test_index": index, "generated_candidates": len(candidates),
                   "distinct_candidate_behaviors": len(behavior_hashes), "no_candidates": not candidates,
                   "raw_candidate_oracle_exact": raw_exact,
                   "live_base_attempt1_exact": base["attempt_1"] == truth,
                   "live_base_attempt2_exact": base["attempt_2"] == truth,
                   "live_base_pass2_exact": truth in (base["attempt_1"], base["attempt_2"])}
            row["candidate_or_base_oracle_exact"] = raw_exact or row["live_base_pass2_exact"]
            for policy in POLICIES:
                selected = dispatches[policy]["submission"][task_id][index]
                sources = dispatches[policy]["decisions"][task_id]["selected_sources"][index]
                require(set(selected) == {"attempt_1", "attempt_2"} and len(sources) == 2,
                        "frozen selected attempt schema differs")
                require(selected["attempt_1"] == base["attempt_1"], "live Attempt 1 was not preserved")
                for slot, source in enumerate(sources, 1):
                    if source.startswith("live_base_"):
                        require(source in ("live_base_1", "live_base_2"), "unknown live-base source")
                        expected_grid = base["attempt_" + source[-1]]
                    else:
                        require(source in eligible[policy], "selected source is outside frozen eligible pool")
                        expected_grid = eligible[policy][source][index]
                    require(selected[f"attempt_{slot}"] == expected_grid, "selected source grid differs")
                selected_exact = truth in (selected["attempt_1"], selected["attempt_2"])
                eligible_exact = any(outputs[index] == truth for outputs in eligible[policy].values())
                require(not selected_exact or row["candidate_or_base_oracle_exact"],
                        "selected exact output absent from recorded prediction pool")
                prefix = policy + "_"
                row.update({prefix + "attempt1_exact": selected["attempt_1"] == truth,
                            prefix + "pass2_exact": selected_exact,
                            prefix + "eligible_pool_oracle_exact": eligible_exact,
                            prefix + "missed_raw_candidate_coverage": raw_exact and not selected_exact,
                            prefix + "missed_eligible_coverage": eligible_exact and not selected_exact,
                            prefix + "filtered_correct_candidate_and_missed": raw_exact and not eligible_exact and not selected_exact,
                            prefix + "missed_live_base_coverage": row["live_base_pass2_exact"] and not selected_exact,
                            prefix + "source1": sources[0], prefix + "source2": sources[1]})
            local_rows.append(row)
            rows.append(row)
        task = {"task_id": task_id, "test_outputs": len(truths), "generated_candidates": len(candidates),
                "no_candidates": not candidates,
                "raw_candidate_oracle_all_outputs": all(r["raw_candidate_oracle_exact"] for r in local_rows),
                "one_raw_candidate_solves_all_outputs": any(c["test_outputs"] == truths for c in candidates),
                "live_base_attempt1_all_outputs": all(r["live_base_attempt1_exact"] for r in local_rows),
                "live_base_pass2_all_outputs": all(r["live_base_pass2_exact"] for r in local_rows),
                "candidate_or_base_oracle_all_outputs": all(r["candidate_or_base_oracle_exact"] for r in local_rows)}
        for policy in POLICIES:
            task[policy + "_attempt1_all_outputs"] = all(r[policy + "_attempt1_exact"] for r in local_rows)
            task[policy + "_pass2_all_outputs"] = all(r[policy + "_pass2_exact"] for r in local_rows)
            task[policy + "_eligible_pool_oracle_all_outputs"] = all(r[policy + "_eligible_pool_oracle_exact"] for r in local_rows)
            task[policy + "_one_eligible_behavior_solves_all_outputs"] = any(v == truths for v in eligible[policy].values())
        task_rows.append(task)
        del record, candidates
    require(second_receipt == first_receipt and len(rows) == 172 and len(task_rows) == 120,
            "diagnostic streaming passes or output membership differ")
    policy_metrics = {}
    for policy in POLICIES:
        first = metric(rows, task_rows, policy + "_attempt1_exact", policy + "_attempt1_all_outputs")
        second = metric(rows, task_rows, policy + "_pass2_exact", policy + "_pass2_all_outputs")
        score, final = scores[policy], audit["policy_results"][policy]
        require(first["exact_outputs"] == score["output_weighted_pass_at_1"]["exact"] == final["pass_at_1"]["exact"] and
                second["exact_outputs"] == score["output_weighted_pass_at_2"]["exact"] == final["pass_at_2"]["exact"] and
                first["whole_tasks"] == score["whole_task_pass_at_1"]["exact"] == final["whole_task_pass_at_1"]["exact"] and
                second["whole_tasks"] == score["whole_task_pass_at_2"]["exact"] == final["whole_task_pass_at_2"]["exact"],
                "diagnostic selected exact totals differ from final scores")
        policy_metrics[policy] = {
            "frozen_selected_pass1": first, "frozen_selected_pass2": second,
            "selected_totals_agree_with_final_scores": True,
            "eligible_pool_label_aware_oracle": metric(rows, task_rows, policy + "_eligible_pool_oracle_exact", policy + "_eligible_pool_oracle_all_outputs"),
            "one_eligible_behavior_solves_entire_task": sum(t[policy + "_one_eligible_behavior_solves_all_outputs"] for t in task_rows),
            "outputs_covered_by_raw_candidate_but_missed": sum(r[policy + "_missed_raw_candidate_coverage"] for r in rows),
            "outputs_covered_by_eligible_behavior_but_missed": sum(r[policy + "_missed_eligible_coverage"] for r in rows),
            "outputs_correct_in_raw_pool_filtered_out_and_missed": sum(r[policy + "_filtered_correct_candidate_and_missed"] for r in rows),
            "outputs_covered_by_live_base_but_missed": sum(r[policy + "_missed_live_base_coverage"] for r in rows),
            "outputs_covered_by_candidate_or_base_but_missed": sum(r["candidate_or_base_oracle_exact"] and not r[policy + "_pass2_exact"] for r in rows),
            "outputs_missing_recorded_candidate_and_base_coverage": sum(not r["candidate_or_base_oracle_exact"] for r in rows)}
    for path, original in bound.items():
        require(identity(path) == original, f"authenticated input changed: {path.name}")
    require(identity(solutions_path) == target_identity, "diagnostic targets changed")
    require(source_check(root, snapshot) == source_mtimes_before, "source mtime changed during diagnostic")
    require(bindings == {"code_hash": engine.code_hash(), "bank_hash": engine.bank_hash(),
                         "prediction_hash": solver.prediction_hash()}, "source bindings changed")
    report = {
        "schema": "komorebi.block17.post-score-label-aware-candidate-diagnostic.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "label_aware_post_score_diagnostic": True, "oracle_coverage_is_not_a_solver_score": True,
        "tasks": 120, "test_outputs": 172,
        "targets_opened_only_after_final_scores_and_complete_census_authentication": True,
        "compiler_dispatcher_ranking_and_program_execution_calls": 0,
        "source_budgets_policies_predictions_and_census_unchanged": True,
        "source_content_inventory_sizes_and_hashes_verified": True,
        "source_mtimes_unchanged_during_diagnostic": True,
        "source_mtime_differences_from_original_release_snapshot":
            sum(value != snapshot[name]["mtime_ns"] for name, value in source_mtimes_before.items()),
        "source_mtime_scope": "Exact source contents, inventory and sizes must match the original snapshot. Extraction mtimes may differ after relocation, but must stay unchanged throughout this diagnostic.",
        "pre_score_freeze_content_hash": freeze["content_hash"],
        "final_scoring_audit_content_hash": audit["content_hash"], "source_bindings": bindings,
        "census_authentication": first_receipt, "fresh_run_hash": RUN_HASH,
        "source_snapshot_sha256": SOURCE_SNAPSHOT_SHA256, "reviewed_stream_adapter_sha256": PARSER_SHA256,
        "solutions_post_score_identity": target_identity,
        "generated_candidate_count": generated_total,
        "generated_candidates_by_provider": dict(sorted(generated_by_provider.items())),
        "no_candidate_tasks": sum(t["no_candidates"] for t in task_rows),
        "no_candidate_outputs": sum(r["no_candidates"] for r in rows),
        "raw_candidate_pool_label_aware_oracle": metric(rows, task_rows, "raw_candidate_oracle_exact", "raw_candidate_oracle_all_outputs"),
        "tasks_with_one_generated_candidate_solving_all_outputs": sum(t["one_raw_candidate_solves_all_outputs"] for t in task_rows),
        "recorded_live_base_diagnostic": {
            "attempt1": metric(rows, task_rows, "live_base_attempt1_exact", "live_base_attempt1_all_outputs"),
            "pass2": metric(rows, task_rows, "live_base_pass2_exact", "live_base_pass2_all_outputs")},
        "candidate_plus_live_base_label_aware_oracle": metric(rows, task_rows, "candidate_or_base_oracle_exact", "candidate_or_base_oracle_all_outputs"),
        "frozen_policy_comparisons": policy_metrics,
        "retained_non_ok_compiler_receipt_count": len(non_ok_receipts),
        "retained_non_ok_compiler_receipts_by_provider_and_status":
            {p: dict(sorted(counts.items())) for p, counts in sorted(errors_by_provider.items())},
        "retained_non_ok_compiler_receipts": non_ok_receipts,
        "metric_definitions": {
            "raw_candidate_pool_oracle": "At each test position, targets choose any exact grid from the complete recorded candidate pool. Unlimited label-aware selection; never a solver score.",
            "oracle_whole_task": "Every position is covered, potentially by different candidates. The separate one-candidate metric requires one candidate's complete output vector to match.",
            "eligible_pool_oracle": "Uses the authenticated frozen policy's saved behaviors after supersession, repair veto and abstention. No ranking is rerun.",
            "missed_eligible_coverage": "A recorded eligible behavior covers the output but the frozen two-attempt selection misses. This diagnoses ranking or slot allocation, not a newly executed policy.",
            "filtered_and_missed": "The raw pool covers an output, the saved eligible pool does not, and the frozen selection misses; filters/supersession/abstention contribute to this gap.",
            "missing_recorded_coverage": "Neither generated candidates nor either live-base attempt contains the target. It does not prove the task is unsolvable or explain which search stage failed.",
            "retained_errors": "All non-ok compiler receipts, including error/incomplete statuses, remain in the diagnostic and in complete-output scoring."},
        "per_task": task_rows, "ledger_path": str(ledger_path), "integrity_pass": True}
    output.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report["ledger_sha256"] = sha256(ledger_path)
    report["content_hash"] = digest(report)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"diagnostic": str(output), "label_aware_diagnostic_not_solver_score": True,
                      "generated_candidates": generated_total, "no_candidate_tasks": report["no_candidate_tasks"],
                      "no_candidate_outputs": report["no_candidate_outputs"], "integrity_pass": True}, indent=2))


if __name__ == "__main__":
    main()
