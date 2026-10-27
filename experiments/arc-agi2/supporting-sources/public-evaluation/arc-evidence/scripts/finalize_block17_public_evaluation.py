"""Run fixed dispatches and independently score a completed fresh ARC census.

This orchestration script lives outside frozen source. It accepts no policy
selection, waits for no process, and opens target labels only after both fixed
predictions have been authenticated, extracted and sealed in a freeze record.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

POLICIES = ("typed_recent", "typed_supported")


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(path):
    path = Path(path).resolve()
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": file_hash(path)}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value, sealed=False):
    value = dict(value)
    if sealed:
        value.pop("content_hash", None)
        value["content_hash"] = digest(value)
    path = Path(path)
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(json.dumps(value, sort_keys=True, indent=2,
                                   ensure_ascii=False, allow_nan=False) + "\n")
    partial.replace(path)
    return value


def verify_seal(value):
    if value.get("content_hash") != digest({k: v for k, v in value.items()
                                            if k != "content_hash"}):
        raise ValueError("Invalid content seal")


def run(command, cwd, log, env):
    with Path(log).open("w", encoding="utf-8") as handle:
        result = subprocess.run(command, cwd=cwd, env=env,
                                stdout=handle, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Execution failed with exit {result.returncode}; see {log}")


def assert_scan_exited(census):
    for entry in Path("/proc").glob("[0-9]*"):
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\0")
            matching = False
            for index, part in enumerate(argv):
                if part == b"--output" and index + 1 < len(argv):
                    value = Path(os.fsdecode(argv[index + 1]))
                    if not value.is_absolute():
                        try:
                            value = (entry / "cwd").resolve(strict=True) / value
                        except OSError:
                            matching = True  # Fail closed for an unreadable matching scanner cwd.
                            break
                    matching = value.resolve() == census.resolve()
                    break
            if (any(Path(os.fsdecode(part)).name in {"run_scan.py", "supplement_block17_scan.py"}
                    for part in argv[1:] if part) and matching):
                raise RuntimeError("A primary or supplemental scan is still running")
        except (OSError, ProcessLookupError):
            continue


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--source-snapshot", type=Path,
                        help="Authenticated source baseline; defaults to the original current-run snapshot")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    root = workspace / "arc-fullbank/block17"
    evidence = workspace / "arc-evidence"
    snapshot = (args.source_snapshot or
                evidence / "later-source-audit/block17_source_before.json").resolve()
    snapshot_identity = identity(snapshot)
    output = evidence / "fullbank-public-evaluation"
    census = output / "census.json"
    challenges_path = workspace / "arc-offline-data/arc-agi_evaluation_challenges.json"
    solutions_path = workspace / "arc-offline-data/arc-agi_evaluation_solutions.json"
    if not census.is_file() or len(list(census.with_suffix(".tasks").glob("*.json"))) != 120:
        raise RuntimeError("The complete 120-task census and checkpoints are required")
    assert_scan_exited(census)
    challenges = read(challenges_path)
    counts = {k: len(v["test"]) for k, v in challenges.items()}
    if len(counts) != 120 or sum(counts.values()) != 172:
        raise ValueError("Unexpected evaluation membership")
    if any("output" in row for task in challenges.values() for row in task["test"]):
        raise ValueError("Challenge file contains attached query targets")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
           "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    adapter = evidence / "later-source-audit/stream_fresh_block17_dispatch.py"
    before = {"census": identity(census), "challenges": identity(challenges_path)}
    supplemental_metadata = output / "supplemental_scan_metadata.json"
    supplemental = None
    agreement = None
    if (any(evidence.glob("fullbank_evaluation_supplemental*.log")) or
            (output / "scan_process_completion.json").exists()) and not supplemental_metadata.is_file():
        raise ValueError("Supplemental execution provenance exists but its metadata is missing")
    if supplemental_metadata.is_file():
        run([sys.executable, str(evidence / "scripts/authenticate_block17_supplement.py"),
             "--workspace", str(workspace)], root,
            output / "supplemental_final_record_agreement.log", env)
        agreement_path = output / "supplemental_final_record_agreement.json"
        agreement = read(agreement_path)
        verify_seal(agreement)
        if (agreement.get("integrity_pass") is not True or agreement.get("targets_opened") is not False
                or agreement.get("tasks") != 120 or agreement.get("test_outputs") != 172
                or agreement.get("every_supplemental_completion_including_duplicates_matches") is not True
                or agreement["inputs"]["census"] != before["census"]):
            raise ValueError("Supplemental final-record authentication failed")
        supplemental = {"metadata": identity(supplemental_metadata),
                        "process_completion": identity(output / "scan_process_completion.json"),
                        "agreement": identity(agreement_path),
                        "agreement_content_hash": agreement["content_hash"],
                        "global_schedule_equivalence_proven": False}
    started = now()
    dispatches = {}
    audits = {}
    freeze_policies = {}
    for policy in POLICIES:
        command = [sys.executable, str(adapter), "--root", str(root),
                   "--challenges", str(challenges_path), "--census", str(census),
                   "--output-dir", str(output), "--policy", policy]
        run(command, root, output / (policy + "_dispatch.log"), env)
        path = output / (policy + "_dispatch.json")
        dispatch = read(path)
        verify_seal(dispatch)
        audit = read(output / (policy + "_dispatch_audit.json"))
        if (dispatch.get("policy") != policy or dispatch.get("label_access") != "demonstrations_only"
                or dispatch.get("champion_fallback") is not False or not audit.get("integrity_pass")
                or audit.get("records") != 120 or audit.get("test_outputs") != 172):
            raise ValueError("Dispatch metadata or complete membership failed")
        if dispatch.get("census_hash") != audit.get("census_hash"):
            raise ValueError("Dispatch and audit census seals differ")
        if set(dispatch["submission"]) != set(counts) or set(dispatch["decisions"]) != set(counts):
            raise ValueError("Incomplete prediction task membership")
        for key, rows in dispatch["submission"].items():
            if len(rows) != counts[key] or any(set(row) != {"attempt_1", "attempt_2"} for row in rows):
                raise ValueError("Incomplete prediction output membership")
        submission_path = output / (policy + "_submission.json")
        write(submission_path, dispatch["submission"])
        freeze_policies[policy] = {
            "dispatch_sha256": file_hash(path),
            "dispatch_content_hash": dispatch["content_hash"],
            "submission_sha256": file_hash(submission_path),
            "submission_hash": digest(dispatch["submission"]),
            "dispatch_path": str(path), "submission_path": str(submission_path),
            "prediction_hash": dispatch["prediction_hash"],
            "bank_hash": dispatch["bank_hash"], "census_hash": dispatch["census_hash"]}
        dispatches[policy] = dispatch
        audits[policy] = audit
        print(json.dumps({"policy": policy, "prediction_saved": True,
                          "targets_opened": False}), flush=True)
    if audits[POLICIES[0]]["source_before_and_after"] != audits[POLICIES[1]]["source_before_and_after"]:
        raise ValueError("Source identity differs between policies")
    if freeze_policies[POLICIES[0]]["census_hash"] != freeze_policies[POLICIES[1]]["census_hash"]:
        raise ValueError("Policies did not use the same census")
    if before != {"census": identity(census), "challenges": identity(challenges_path)}:
        raise ValueError("Census or input bytes changed between policy dispatches")
    source_audit = output / "source_unchanged_audit.json"
    run([sys.executable, str(evidence / "later-source-audit/verify_block17_unchanged.py"),
         "--root", str(root), "--snapshot", str(snapshot),
         "--output", str(source_audit)], root, output / "source_unchanged_audit.log", env)
    source_report = read(source_audit)
    if not source_report.get("unchanged"):
        raise ValueError("Frozen source changed")
    if identity(snapshot) != snapshot_identity:
        raise ValueError("Source baseline changed during dispatch")
    assert_scan_exited(census)
    if supplemental is not None:
        if identity(supplemental_metadata) != supplemental["metadata"]:
            raise ValueError("Supplemental metadata changed before freezing")
        if identity(output / "scan_process_completion.json") != supplemental["process_completion"]:
            raise ValueError("Owning-session completion receipt changed before freezing")
        if identity(output / "supplemental_final_record_agreement.json") != supplemental["agreement"]:
            raise ValueError("Supplemental agreement receipt changed before freezing")
        for checkpoint in agreement["final_checkpoint_identities"].values():
            if identity(Path(checkpoint["path"])) != checkpoint:
                raise ValueError("Final checkpoint changed after supplemental agreement gate")
    freeze = write(output / "predictions_before_scoring.json", {
        "schema": "komorebi.block17.public-evaluation-pre-score-freeze.v1",
        "frozen_at_utc": now(), "dispatch_started_utc": started,
        "targets_opened": False,
        "label_order_scope": "This fresh full-bank dispatch and scoring workflow; earlier project evaluation exposure is retained as a limitation.",
        "both_predictions_authenticated": True, "primary_policy": POLICIES[0],
        "secondary_control_policy": POLICIES[1], "policy_sequence": list(POLICIES),
        "tasks": 120, "test_outputs": 172, "inputs": before,
        "source_snapshot": snapshot_identity,
        "supplemental_execution": supplemental,
        "source_unchanged": source_report, "policies": freeze_policies}, sealed=True)
    verify_seal(freeze)
    labels_first_scoring_started = now()
    scores = {}
    for policy in POLICIES:
        run([sys.executable, str(evidence / "scripts/score_arc_submission.py"),
             "--challenges", str(challenges_path), "--solutions", str(solutions_path),
             "--submission", str(output / (policy + "_submission.json")),
             "--output", str(output / (policy + "_score.json")),
             "--ledger", str(output / (policy + "_ledger.csv")),
             "--label", "Fresh frozen Block17 all-bank public evaluation; " + policy,
             "--split", "evaluation"], workspace, output / (policy + "_score.log"), env)
        scores[policy] = read(output / (policy + "_score.json"))
    # A second direct comparison is independent of the scoring CLI calculations.
    truths = read(solutions_path)
    if set(truths) != set(counts):
        raise ValueError("Target membership differs")
    for key in counts:
        if len(truths[key]) != counts[key]:
            raise ValueError("Target output positions differ")
    policy_reports = {}
    for policy in POLICIES:
        rows = dispatches[policy]["submission"]
        exact1 = sum(rows[k][i]["attempt_1"] == target for k in truths for i, target in enumerate(truths[k]))
        exact2 = sum(any(rows[k][i][a] == target for a in ("attempt_1", "attempt_2"))
                     for k in truths for i, target in enumerate(truths[k]))
        whole1 = sum(all(rows[k][i]["attempt_1"] == target for i, target in enumerate(truths[k])) for k in truths)
        whole2 = sum(all(any(rows[k][i][a] == target for a in ("attempt_1", "attempt_2"))
                         for i, target in enumerate(truths[k])) for k in truths)
        score = scores[policy]
        if (score["tasks"] != 120 or score["test_outputs"] != 172
                or score["output_weighted_pass_at_1"]["exact"] != exact1
                or score["output_weighted_pass_at_2"]["exact"] != exact2
                or score["whole_task_pass_at_1"]["exact"] != whole1
                or score["whole_task_pass_at_2"]["exact"] != whole2):
            raise ValueError("Independent direct comparison differs from score artifact")
        with (output / (policy + "_ledger.csv")).open(newline="") as stream:
            ledger = list(csv.DictReader(stream))
        if (len(ledger) != 172 or sum(r["attempt_1_exact"] == "True" for r in ledger) != exact1
                or sum(r["pass_at_2_exact"] == "True" for r in ledger) != exact2):
            raise ValueError("Per-test ledger totals differ")
        if (file_hash(output / (policy + "_dispatch.json")) != freeze_policies[policy]["dispatch_sha256"]
                or file_hash(output / (policy + "_submission.json")) != freeze_policies[policy]["submission_sha256"]):
            raise ValueError("Predictions changed after pre-score freeze")
        policy_reports[policy] = {"pass_at_1": {"exact": exact1, "total": 172, "fraction": exact1 / 172},
            "pass_at_2": {"exact": exact2, "total": 172, "fraction": exact2 / 172},
            "whole_task_pass_at_1": {"exact": whole1, "total": 120},
            "whole_task_pass_at_2": {"exact": whole2, "total": 120},
            "task_mean_pass_at_2_fraction": score["task_mean_pass_at_2_fraction"],
            "second_attempt_incremental_exact": exact2 - exact1,
            "dispatch": identity(output / (policy + "_dispatch.json")),
            "submission": identity(output / (policy + "_submission.json")),
            "dispatch_content_hash": dispatches[policy]["content_hash"],
            "submission_hash": digest(rows), "score": identity(output / (policy + "_score.json")),
            "ledger": identity(output / (policy + "_ledger.csv")),
            "activated_tasks": sum(bool(d["activated"]) for d in dispatches[policy]["decisions"].values())}
    first_preserved = all(dispatches[POLICIES[0]]["submission"][k][i]["attempt_1"] ==
                          dispatches[POLICIES[1]]["submission"][k][i]["attempt_1"]
                          for k in counts for i in range(counts[k]))
    if not first_preserved:
        raise ValueError("Fixed policy attempt-1 outputs differ")
    audit = write(output / "independent_scoring_audit.json", {
        "schema": "komorebi.block17.fresh-public-evaluation-independent-audit.v1",
        "generated_at_utc": now(), "scope": "Fresh complete-bank compiler scan followed by fixed frozen-policy dispatch and independent public-evaluation scoring.",
        "primary_policy": POLICIES[0], "secondary_control_policy": POLICIES[1],
        "tasks": 120, "test_outputs": 172, "membership_complete": True,
        "targets_first_scoring_started_utc": labels_first_scoring_started,
        "both_predictions_saved_and_authenticated_before_labels": True,
        "pre_score_freeze": {**identity(output / "predictions_before_scoring.json"), "content_hash": freeze["content_hash"]},
        "census": {**before["census"], "content_hash": audits[POLICIES[0]]["census_hash"],
                   "run_hash": audits[POLICIES[0]]["fresh_run_hash"]},
        "challenges": before["challenges"], "solutions_after_prediction_freeze": identity(solutions_path),
        "source_bindings": audits[POLICIES[0]]["source_before_and_after"],
        "source_snapshot_verification": source_report,
        "source_snapshot": snapshot_identity,
        "supplemental_execution": supplemental,
        "frozen_source_files_unchanged": True,
        "fresh_candidates": audits[POLICIES[0]]["candidates"],
        "retained_compiler_error_receipts": audits[POLICIES[0]]["error_receipt_count"],
        "compilation_error_free": audits[POLICIES[0]]["compilation_error_free"],
        "compiler_receipt_ledger": str(output / (POLICIES[0] + "_dispatch_audit.json")),
        "no_champion_fallback": True, "policies_unchanged_before_scoring": True,
        "attempt_1_equal_between_policies": first_preserved,
        "scorer_has_zero_solver_calls": True,
        "score_and_ledgers_rechecked_with_direct_grid_comparison": True,
        "policy_results": policy_reports,
        "metric": "Output-weighted exact pass@2 across all 172 test outputs; whole-task and task-mean rates are supplementary.",
        "limitations": ["Public evaluation was previously inspected in the project; this is a fresh frozen execution, not a hidden or private benchmark score.",
                        "Trusted-code label isolation, not an adversarial filesystem sandbox.",
                        "Dispatcher aggregation uses a separately reviewed streaming adapter; underlying frozen per-task dispatcher remains unchanged.",
                        "Retained compiler-error receipts are reported separately from complete-output scoring.",
                        "Where supplemental scheduling was used, actual completion/checkpoint/census hashes agree; global scheduler or process-history equivalence is not proven."],
        "integrity_pass": True}, sealed=True)
    print(json.dumps({"audit": str(output / "independent_scoring_audit.json"),
                      "primary": policy_reports[POLICIES[0]]["pass_at_2"],
                      "control": policy_reports[POLICIES[1]]["pass_at_2"],
                      "source_unchanged": True, "integrity_pass": audit["integrity_pass"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
