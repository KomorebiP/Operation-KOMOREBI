"""Audit the completed six-task diagnostic and execute only its new program.

No compilers, dispatchers, scoring routines or query-solution files are used.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
WORKSPACE = Path(__file__).resolve().parents[2]
PINNED_INPUTS = {
    "original_source_identity.json": "5aa8264d16fa5e73efe8d95bc40f845e0366f7fb2335c7d8f24dba7c625f31b7",
    "expected_records.json": "dd7b78e4ae1eff42ea75556cae070e7fc4f9ac6580599a69b1834de74b424594",
    "selected_challenges.json": "dd1c53c1c4144dde0d5e0f50b8d4332d21e2f562cdedb083927c1690385c3a78",
    "selection_audit.json": "206c207838c9fe21f00642303fe8216344520f3399fa2a75e6376fdf436205f9",
    "fresh_patched_training.json": "ac98642581f336a66b61e3dbfd7c9db058e4f7fddacd449411c7b0460f67e121",
    "corrected_fullbank_sample_review.json": "8b639cd1bf4bb2427776a20d7708514f1100b6350b677e150a30d6028b8f5433",
}
PATCHES = {
    "entrants13/extraction.py": "e7e99cbb85f4b1a288f2145d38194b2bd7f44f8ee7212971c3410d497197e9a2",
    "bank13.json": "294d07bb868406cddda604f348f70a22c78945f1da9444a443889659f83cc020",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def identity(path):
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": file_sha(path)}


def seal(value):
    assert value.get("content_hash") == digest({k: v for k, v in value.items() if k != "content_hash"}), "bad seal"


def metadata(root):
    paths = sorted(p for p in root.rglob("*") if p.is_file())
    assert not any(p.is_symlink() for p in root.rglob("*")), "source symlink"
    return {str(p.relative_to(root)): {"bytes": p.stat().st_size, "mtime_ns": p.stat().st_mtime_ns} for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=WORKSPACE / "arc-limitfix-installer-check/block17")
    parser.add_argument("--diagnosis-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source, evidence = args.source_root.resolve(), args.diagnosis_root.resolve()
    output = (args.output or evidence / "corrected_fullbank_sample_independent_audit.json").resolve()
    assert not output.exists(), "output already exists"
    assert source != output.parent and source not in output.parents, "output inside source"
    start = time.monotonic()
    source_before = metadata(source)
    inputs = {name: identity(evidence / name) for name in PINNED_INPUTS}
    for name, expected in PINNED_INPUTS.items():
        assert inputs[name]["sha256"] == expected, name
    data = {name: json.loads((evidence / name).read_text()) for name in PINNED_INPUTS}
    baseline = data["original_source_identity.json"]["files"]
    assert len(baseline) == len(source_before) == 388 and set(baseline) == set(source_before)
    source_hashes = {name: file_sha(source / name) for name in baseline}
    assert {name for name in baseline if baseline[name] != source_hashes[name]} == set(PATCHES)
    for name, expected in PATCHES.items():
        assert source_hashes[name] == expected, name
    vendor = json.loads((source / "vendor_manifest.json").read_text())
    bank13 = json.loads((source / "bank13.json").read_text())
    modern = json.loads((source / "bank14_15.json").read_text())
    for name, expected in vendor.items():
        assert source_hashes[name] == expected
    for name, expected in bank13.items():
        assert source_hashes[f"entrants13/{name}.py"] == expected
    for name, entry in modern.items():
        assert source_hashes[f"entrants/{name}.py"] == entry["sha256"]
    code_hash = digest({name: source_hashes[name] for name in ("engine.py", "legacy.py", "action_adapter.py", "contract.py", "memo.py")})
    bank_hash = digest({"vendor_manifest.json": vendor, "bank13.json": bank13, "bank14_15.json": modern})
    census = data["fresh_patched_training.json"]
    review = data["corrected_fullbank_sample_review.json"]
    selection = data["selection_audit.json"]
    for value in (census, review, selection):
        seal(value)
    assert census["code_hash"] == review["code_hash"] == code_hash
    assert census["bank_hash"] == review["bank_hash"] == bank_hash
    assert census["scope"] == "all_banks" and census["champion_fallback"] is False
    assert census["label_access"] == "demonstrations_only"
    assert review["query_targets_opened"] is False and selection["query_targets_opened"] is False
    assert review["census_file_sha256"] == inputs["fresh_patched_training.json"]["sha256"]
    assert review["census_content_hash"] == census["content_hash"]
    challenges, expected = data["selected_challenges.json"], data["expected_records.json"]
    assert len(challenges) == 6 and set(challenges) == set(expected) == set(census["records"])
    for task in challenges.values():
        assert set(task) == {"train", "test"}
        assert all(set(row) == {"input", "output"} for row in task["train"])
        assert all(set(row) == {"input"} for row in task["test"])
    assert digest(challenges) == census["challenges_hash"]
    assert digest({"code": code_hash, "bank": bank_hash, "challenges": challenges,
                   "include_new": True, "limits": census["limits"]}) == census["run_hash"]
    for name in ("expected_records.json", "selected_challenges.json"):
        assert selection["outputs"][name]["sha256"] == inputs[name]["sha256"]
    fresh_original = {}
    original_comparisons = {}
    for path in sorted((evidence / "fresh_original_training").glob("*/comparison.json")):
        value = json.loads(path.read_text()); seal(value)
        child = value["child_report"]; seal(child)
        assert value["exit_code"] == 0 and value["external_watchdog_timeout"] is False
        assert value["equivalence"] is True and child["query_targets_opened"] is False
        record_path = path.parent / "fresh_record.json"
        assert file_sha(record_path) == child["record"]["sha256"]
        record = json.loads(record_path.read_text()); seal(record)
        assert record == expected[value["task_id"]]
        fresh_original[value["task_id"]] = record
        original_comparisons[value["task_id"]] = {"comparison": identity(path), "record": identity(record_path)}
    assert set(fresh_original) == set(expected)
    provider_names = set(bank13) | set(modern) | {"core_blocks2_4"} | {f"legacy_block{i}" for i in (6, 7, 8, 9, 10, 11, 12)}
    assert len(provider_names) == 77
    checks, additions = {}, []
    for task_id in sorted(challenges):
        old, new = expected[task_id], census["records"][task_id]
        seal(old); seal(new)
        assert old["content_hash"] == selection["selected_task_record_hashes"][task_id]
        assert old["task_semantic_hash"] == new["task_semantic_hash"] == digest(challenges[task_id])
        assert set(old["receipts"]) == set(new["receipts"]) == provider_names
        assert old["base"] == new["base"]
        before_candidates = [c for c in old["candidates"] if c["entrant"] != "extraction"]
        after_candidates = [c for c in new["candidates"] if c["entrant"] != "extraction"]
        assert before_candidates == after_candidates
        assert {k: v for k, v in old["receipts"].items() if k != "extraction"} == {k: v for k, v in new["receipts"].items() if k != "extraction"}
        assert not any(c["entrant"] == "extraction" for c in old["candidates"])
        for candidate in new["candidates"]:
            assert candidate["candidate_hash"] == digest({k: v for k, v in candidate.items() if k != "candidate_hash"})
            assert candidate["behavior_hash"] == digest(candidate["test_outputs"])
            if "origin_candidate_hash" in candidate:
                assert candidate["origin_candidate_hash"] == digest({k: v for k, v in candidate.items() if k not in {"candidate_hash", "origin_candidate_hash", "source_block"}})
        added = [c for c in new["candidates"] if c["entrant"] == "extraction"]
        additions.extend((task_id, c) for c in added)
        checks[task_id] = {"original_candidates": len(old["candidates"]), "corrected_candidates": len(new["candidates"]),
                           "all_original_candidates_and_relative_order_preserved": True,
                           "all76_other_receipts_and_base_exact": True, "new_extraction_candidates": len(added),
                           "original_unique_query_behaviors": len({c["behavior_hash"] for c in old["candidates"]}),
                           "corrected_unique_query_behaviors": len({c["behavior_hash"] for c in new["candidates"]}),
                           "corrected_record_hash": new["content_hash"]}
    assert len(additions) == 1 and additions[0][0] == "9565186b"
    task_id, candidate = additions[0]
    spec = importlib.util.spec_from_file_location("corrected_sample_extraction", source / "entrants13/extraction.py")
    extraction = importlib.util.module_from_spec(spec); sys.modules[spec.name] = extraction; spec.loader.exec_module(extraction)
    assert not hasattr(extraction, "replay_program")
    program = json.loads(json.dumps(candidate["program"]))
    replay = []
    for split in ("train", "test"):
        for index, example in enumerate(challenges[task_id][split]):
            result = [list(row) for row in extraction._execute(extraction._grid(example["input"]), program, extraction._Limits().max_objects)]
            assert result == candidate[f"{split}_outputs"][index]
            if split == "train":
                assert result == example["output"]
            replay.append({"split": split, "index": index, "output_hash": digest(result),
                           "stored_prediction_exact": True, "demonstration_exact": True if split == "train" else None})
    assert candidate["execution_replay"]["status"] == "not_supplied"
    old = expected[task_id]
    matching = [c for c in old["candidates"] if c["test_outputs"] == candidate["test_outputs"]]
    base_matches = {slot: [row[slot] for row in old["base"]] == candidate["test_outputs"] for slot in ("attempt_1", "attempt_2")}
    assert len(matching) == 19 and base_matches == {"attempt_1": True, "attempt_2": False}
    source_after = metadata(source)
    assert source_before == source_after
    for name, before in inputs.items():
        assert identity(evidence / name) == before
    body = {
        "schema": "block17.limitfix.corrected_fullbank_sample_independent_audit.v1",
        "recorded_utc": datetime.now(timezone.utc).isoformat(), "integrity_pass": True,
        "audit_script_sha256": file_sha(Path(__file__)), "elapsed_seconds": time.monotonic() - start,
        "scope": "Completed6 selected training tasks; record preservation and one native-program re-execution. No accuracy measurement.",
        "source_root": str(source), "source_files_authenticated": len(source_before),
        "source_content_matches_original388_except_exact2_patches": True,
        "source_before_after_inventory_sizes_mtimes_identical": True,
        "source_content_hash_manifest_digest": digest(source_hashes),
        "source_patch_pins": PATCHES, "vendor_pins_checked": len(vendor), "native_registry_pins_checked": len(bank13) + len(modern),
        "code_hash": code_hash, "bank_hash": bank_hash, "run_hash": census["run_hash"],
        "inputs": inputs, "original_fresh_comparison_inputs": original_comparisons,
        "original_candidates": sum(len(r["candidates"]) for r in expected.values()),
        "corrected_candidates": sum(len(r["candidates"]) for r in census["records"].values()),
        "all342_original_candidates_preserved": True, "all456_non_extraction_receipts_and6_bases_preserved": True,
        "all6_fresh_original_records_equal_expected_cached_records": True, "checks": checks,
        "new_candidate": {"task_id": task_id, "candidate_hash": candidate["candidate_hash"], "family": candidate["family"],
                          "program": program, "behavior_hash": candidate["behavior_hash"], "stored_query_predictions": candidate["test_outputs"],
                          "native_same_process_serialized_program_reexecution": replay,
                          "production_replay_hook": None, "production_replay_status": "not_supplied",
                          "query_truth_opened_or_compared": False,
                          "original_candidates_with_same_query_behavior": len(matching),
                          "matching_original_candidate_hashes": [c["candidate_hash"] for c in matching],
                          "matching_original_providers": sorted({c["entrant"] for c in matching}),
                          "original_base_complete_query_behavior_matches": base_matches,
                          "adds_new_query_output_coverage_in_this_sample": False},
        "query_targets_opened": False, "compilers_or_dispatchers_called": 0, "new_evaluation_score": None,
        "limitations": ["Training tasks were deliberately selected for diagnostic provider coverage; not a representative evaluation.",
                        "Exact demo replay and stored-query reproduction do not establish query correctness.",
                        "Same-process native execution is distinct from a production replay hook or independent interpreter.",
                        "Restored source content was fully hashed before the audit; inventory/sizes/mtimes were checked afterward."],
    }
    body["content_hash"] = digest(body)
    output.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"integrity_pass": True, "output": identity(output), "original_candidates": body["original_candidates"],
                      "corrected_candidates": body["corrected_candidates"], "native_executions": len(replay),
                      "added_new_query_behavior": False, "elapsed_seconds": body["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
