"""Authenticate final Block17 checkpoints/census against supplemental receipts.

This external gate runs only after both scanner processes have exited. It reads
no target files and executes no compiler, dispatcher, ranking or program. It
verifies all final checkpoint seals and the original whole-census semantic seal,
then requires every supplemental completion, including duplicates, to agree.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys

COMPLETIONS = {"checkpoint_written", "duplicate_identical_not_overwritten"}
SCANNERS = {"run_scan.py", "supplement_block17_scan.py"}


def targets_census(argv, entry, census):
    for index, part in enumerate(argv):
        if part == b"--output" and index + 1 < len(argv):
            value = Path(os.fsdecode(argv[index + 1]))
            if not value.is_absolute():
                try:
                    value = (entry / "cwd").resolve(strict=True) / value
                except OSError:
                    # A matching scanner cannot be excluded when cwd is unreadable.
                    return True
            return value.resolve() == census.resolve()
    return False


def scanners_exited(census):
    for entry in Path("/proc").glob("[0-9]*"):
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\0")
            if (any(Path(os.fsdecode(part)).name in SCANNERS for part in argv[1:] if part)
                    and targets_census(argv, entry, census)):
                raise ValueError("A primary or supplemental scanner is still running")
        except (OSError, ProcessLookupError):
            continue


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def completion_agreement(metadata, records, checkpoint_hashes):
    """Check every completion event separately; repeated events cannot be lost."""
    active = set()
    started = set()
    checked = []
    skipped = []
    reserved = set(metadata["reserved_active_task_ids"])
    require(len(reserved) == len(metadata["reserved_active_task_ids"]) and reserved <= set(records),
            "Reserved supplemental task membership is duplicated or unknown")
    require(type(metadata["initial_missing"]) is int and
            len(reserved) <= metadata["initial_missing"] <= len(records),
            "Initial missing count is outside the authenticated task set")
    for index, event in enumerate(metadata["events"]):
        key = event["task_id"]
        require(key in records and key not in reserved, "Invalid supplemental task membership")
        kind = event["event"]
        if kind == "started":
            require(key not in started and key not in skipped,
                    "Supplemental task was started more than once or after being skipped")
            started.add(key)
            active.add(key)
        elif kind in COMPLETIONS:
            require(key in active, "Completion has no matching active supplemental task")
            require(isinstance(event.get("record_hash"), str), "Completion lacks its record hash")
            require(event["record_hash"] == records[key] == checkpoint_hashes[key],
                    "Supplemental completion differs from final checkpoint or census: " + key)
            checked.append({"event_index": index, "task_id": key, "event": kind,
                            "record_hash": event["record_hash"]})
            active.remove(key)
        elif kind == "skip_existing":
            require(key not in active and key not in started and key not in skipped,
                    "Invalid or duplicated skip-existing event ordering")
            require("record_hash" not in event, "Unexpected hash on skip-existing event")
            skipped.append(key)
        else:
            raise ValueError("Unknown supplemental event: " + str(kind))
    require(not active, "Supplemental metadata contains unfinished tasks")
    require(len(started | set(skipped)) == metadata["initial_missing"] - len(reserved),
            "Terminal supplemental metadata does not cover its entire original pending scope")
    return checked, skipped


def authenticated_census(engine, adapter, clean, census, expected_run_hash):
    """Retain one record pair at a time; authenticate the entire canonical seal."""
    import hashlib
    expected_files = {engine.contract.digest(key) + ".json" for key in clean}
    checkpoints = census.with_suffix(".tasks")
    require({p.name for p in checkpoints.glob("*.json")} == expected_files,
            "Final checkpoint membership differs from the full challenge set")
    canonical = engine.contract.canonical_json
    whole = hashlib.sha256()
    whole.update(b"{")
    first_top = True
    previous_top = None
    header = {}
    records = {}
    checkpoint_hashes = {}
    checkpoint_identities = {}
    stream = adapter.JSONStream(census)
    try:
        stream.expect("{")
        while stream.peek() != "}":
            key = stream.value()
            require(isinstance(key, str) and (previous_top is None or key > previous_top),
                    "Census keys are not unique and sorted")
            previous_top = key
            stream.expect(":")
            if key != "content_hash":
                if not first_top:
                    whole.update(b",")
                whole.update(canonical(key).encode("utf-8") + b":")
                first_top = False
            if key == "records":
                stream.expect("{")
                whole.update(b"{")
                previous_record = None
                first_record = True
                while stream.peek() != "}":
                    task_id = stream.value()
                    require(isinstance(task_id, str) and (previous_record is None or task_id > previous_record),
                            "Record keys are not unique and sorted")
                    previous_record = task_id
                    stream.expect(":")
                    record = stream.value()
                    require(task_id in clean, "Unexpected census task")
                    engine.verify(record)
                    require(record["task_semantic_hash"] == engine.contract.digest(clean[task_id]),
                            "Census record does not match sanitized inputs")
                    adapter.validate_test_membership(engine, task_id, clean[task_id], record)
                    if not first_record:
                        whole.update(b",")
                    whole.update(canonical(task_id).encode("utf-8") + b":" + canonical(record).encode("utf-8"))
                    first_record = False
                    records[task_id] = record["content_hash"]
                    path = checkpoints / (engine.contract.digest(task_id) + ".json")
                    before = adapter.file_identity(path)
                    item = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=adapter.no_duplicates)
                    engine.verify(item)
                    engine.verify(item["record"])
                    require(item["run_hash"] == expected_run_hash, "Final checkpoint has wrong run binding")
                    require(item["record"]["task_semantic_hash"] == record["task_semantic_hash"],
                            "Final checkpoint semantic input differs")
                    checkpoint_hashes[task_id] = item["record"]["content_hash"]
                    require(checkpoint_hashes[task_id] == records[task_id],
                            "Final checkpoint and census differ: " + task_id)
                    require(adapter.file_identity(path) == before, "Final checkpoint changed during authentication")
                    checkpoint_identities[task_id] = before
                    del item, record
                    if len(records) % 25 == 0:
                        print(json.dumps({"authenticated_records": len(records), "target_access": False}), flush=True)
                    separator = stream.peek()
                    if separator == ",":
                        stream.expect(",")
                    else:
                        require(separator == "}", "Invalid census record delimiter")
                stream.expect("}")
                whole.update(b"}")
            else:
                value = stream.value()
                header[key] = value
                if key != "content_hash":
                    whole.update(canonical(value).encode("utf-8"))
            separator = stream.peek()
            if separator == ",":
                stream.expect(",")
            else:
                require(separator == "}", "Invalid census header delimiter")
        stream.expect("}")
        require(not stream.peek(), "Trailing census content")
        whole.update(b"}")
        require(whole.hexdigest() == header.get("content_hash"), "Whole census semantic seal differs")
        require(set(records) == set(clean), "Whole census task membership differs")
        require(header.get("schema") == "komorebi.block17.live_census.v1", "Wrong census schema")
        require(header.get("scope") == "all_banks", "Incomplete census bank scope")
        require(header.get("label_access") == "demonstrations_only" and header.get("champion_fallback") is False,
                "Wrong census label scope or fallback")
        require(header.get("run_hash") == expected_run_hash and header.get("limits") == engine.LIMITS,
                "Census run or limits differ")
        require(header.get("code_hash") == engine.code_hash() and header.get("bank_hash") == engine.bank_hash(),
                "Census source binding differs")
        require(header.get("challenges_hash") == engine.contract.digest(clean), "Census challenge binding differs")
        return header, records, checkpoint_hashes, checkpoint_identities
    finally:
        stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    output = workspace / "arc-evidence/fullbank-public-evaluation"
    census = output / "census.json"
    metadata_path = output / "supplemental_scan_metadata.json"
    process_path = output / "scan_process_completion.json"
    challenge_path = workspace / "arc-offline-data/arc-agi_evaluation_challenges.json"
    root = workspace / "arc-fullbank/block17"
    require(census.is_file(), "Complete census is not available")
    scanners_exited(census)
    sys.path.insert(0, str(root))
    import engine
    require(Path(engine.__file__).resolve() == root / "engine.py", "Wrong engine module origin")
    adapter_path = workspace / "arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py"
    spec = importlib.util.spec_from_file_location("supplement_auth_adapter", adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    identities = {"census": adapter.file_identity(census), "metadata": adapter.file_identity(metadata_path),
                  "process_completion": adapter.file_identity(process_path),
                  "challenges": adapter.file_identity(challenge_path)}
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"), object_pairs_hook=adapter.no_duplicates)
    engine.verify(metadata)
    require(bool(metadata.get("completed_utc")), "Supplemental scan metadata is not terminal")
    process = json.loads(process_path.read_text(encoding="utf-8"), object_pairs_hook=adapter.no_duplicates)
    engine.verify(process)
    require(process.get("schema") == "komorebi.block17.scan-process-completion.v1" and
            process.get("all_scans_and_assembly_stopped") is True,
            "Owning-session completion receipt is not terminal")
    require(process.get("targets_opened") is False and process.get("source_budget_policy_changes") is False,
            "Owning-session receipt has wrong label or source/budget/policy scope")
    require(process.get("census") == identities["census"] and
            process.get("supplemental_metadata") == identities["metadata"],
            "Owning-session receipt binds different final files")
    sessions = process.get("sessions")
    require(isinstance(sessions, list), "Owning-session receipt lacks session evidence")
    roles = [s.get("role") for s in sessions]
    require({"primary_scan", "supplemental_scan"} <= set(roles) <=
            {"primary_scan", "supplemental_scan", "census_assembly"} and len(roles) == len(set(roles)),
            "Owning-session roles are missing or ambiguous")
    for session in sessions:
        require(session.get("stopped") is True and type(session.get("session_id")) is int,
                "Owning-session stop evidence is incomplete")
        require(session.get("exit_code") is None or type(session["exit_code"]) is int,
                "Session exit code must be captured integer or explicit unknown")
        require(isinstance(session.get("completion_evidence"), str) and session["completion_evidence"].strip(),
                "Session completion evidence is empty")
        require(session.get("mode") in {"natural_exit", "redundant_work_interrupt", "checkpoint_only_assembly"},
                "Unknown session completion mode")
    challenge_raw = json.loads(challenge_path.read_text(encoding="utf-8"), object_pairs_hook=adapter.no_duplicates)
    clean = {k: engine.sanitize(t) for k, t in challenge_raw.items()}
    require(len(clean) == 120 and sum(len(t["test"]) for t in clean.values()) == 172,
            "Expected exactly 120 tasks and 172 outputs")
    expected_run = engine.contract.digest({"code": engine.code_hash(), "bank": engine.bank_hash(),
        "challenges": clean, "include_new": True, "limits": engine.LIMITS})
    require(metadata.get("run_hash") == expected_run, "Supplemental run binding differs")
    require(process.get("run_hash") == expected_run, "Owning-session run binding differs")
    require(metadata.get("code_hash") == engine.code_hash() and metadata.get("bank_hash") == engine.bank_hash(),
            "Supplemental source binding differs")
    require(metadata.get("limits") == engine.LIMITS and metadata.get("label_access") == "demonstrations_only",
            "Supplemental limits or label scope differ")
    require(metadata.get("source_changes") is False and metadata.get("policy_changes") is False,
            "Supplemental source or policy change flag is set")
    scheduler = workspace / "arc-evidence/scripts/supplement_block17_scan.py"
    require(metadata.get("scheduler_sha256") == adapter.sha256_file(scheduler), "Scheduler source receipt differs")
    header, records, checkpoint_hashes, checkpoints = authenticated_census(engine, adapter, clean, census, expected_run)
    events, skipped = completion_agreement(metadata, records, checkpoint_hashes)
    require(identities == {"census": adapter.file_identity(census), "metadata": adapter.file_identity(metadata_path),
                          "process_completion": adapter.file_identity(process_path),
                          "challenges": adapter.file_identity(challenge_path)}, "Gate inputs changed during authentication")
    scanners_exited(census)
    report = engine.seal({"schema": "komorebi.block17.supplemental-final-record-agreement.v1",
        "authenticated_utc": datetime.now(timezone.utc).isoformat(), "targets_opened": False,
        "compiler_dispatcher_ranking_program_calls": 0, "tasks": 120, "test_outputs": 172,
        "inputs": identities, "census_content_hash": header["content_hash"],
        "supplemental_metadata_content_hash": metadata["content_hash"], "run_hash": expected_run,
        "scheduler": adapter.file_identity(scheduler), "gate_source": adapter.file_identity(Path(__file__)),
        "both_scans_exited": True, "all_checkpoint_and_census_record_seals_verified": True,
        "owning_session_completion_content_hash": process["content_hash"],
        "owning_session_evidence": sessions,
        "stop_evidence_scope": "Owning execution-session receipts plus available process observations; proc visibility alone is not a global process proof.",
        "all_final_checkpoint_and_census_records_equal": True,
        "every_supplemental_completion_including_duplicates_matches": True,
        "completion_events_checked": len(events), "duplicate_events_checked": sum(e["event"] != "checkpoint_written" for e in events),
        "completion_event_agreements": events, "skip_existing_tasks": skipped,
        "final_record_hashes": records, "final_checkpoint_record_hashes": checkpoint_hashes,
        "final_checkpoint_identities": checkpoints,
        "limitations": ["Record equality authenticates this actual execution; it does not prove global scheduler/process-history equivalence.",
                        "Unexplained execution-session loss and supplemental scheduling are retained in separate provenance."],
        "integrity_pass": True})
    path = output / "supplemental_final_record_agreement.json"
    engine.write(path, report)
    print(json.dumps({"output": str(path), "tasks": 120, "completion_events_checked": len(events),
                      "targets_opened": False, "integrity_pass": True}), flush=True)


if __name__ == "__main__":
    main()
