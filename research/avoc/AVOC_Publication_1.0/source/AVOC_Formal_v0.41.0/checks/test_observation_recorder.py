#!/usr/bin/env python3
"""Independent bounded lifecycle oracle, strict interface tests, real Lean calls."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import calibrate_quote as calibration
import observation_recorder as production

TAG = "observation-recorder-v1"
BATCH = "observation-recorder-batch-v1"
SOURCE_PATHS = (
    "checks/test_observation_recorder.py", "tools/observation_recorder.py",
    "tools/run_recorder_lean.py", "tools/calibrate_quote.py",
    "AVOC/ObservationRecorder.lean", "AVOC/RecorderReveal.lean",
    "AVOC/RecorderCodec.lean", "tools/RecorderMain.lean",
    "examples/observation_recorder/scenarios.json",
    "examples/observation_recorder/registry.json",
    "examples/observation_recorder/complete.json",
    "examples/observation_recorder/pending.json",
)


def equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: {actual!r} != {expected!r}")


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def rejected(call):
    try:
        call()
    except (production.RecorderError, calibration.CalibrationError, ValueError):
        return
    raise AssertionError("invalid input unexpectedly accepted")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def oracle(commands):
    """Dictionary lifecycle automaton independent of the list-based reducer.

    Each ID has exactly one entry (key, phase), phase None for pending, otherwise
    terminal status. Separate insertion/finalization serials reconstruct order.
    """
    lifecycle, intent_serial, terminal_serial = {}, {}, {}
    for index, command in enumerate(commands):
        kind, operation, key = command[:3]
        old = lifecycle.get(operation)
        if kind == "begin":
            if old is None:
                lifecycle[operation] = (key, None)
                intent_serial[operation] = index
            elif old[0] != key:
                return {"status": "rejected", "index": index, "error": "command_rejected"}
        else:
            outcome = command[3]
            if old is None or old[0] != key or old[1] not in (None, outcome):
                return {"status": "rejected", "index": index, "error": "command_rejected"}
            if old[1] is None:
                lifecycle[operation] = (key, outcome)
                terminal_serial[operation] = index
    pending = [[operation, lifecycle[operation][0]]
               for operation in sorted(intent_serial, key=intent_serial.get)
               if lifecycle[operation][1] is None]
    log = [[operation, *lifecycle[operation]]
           for operation in sorted(terminal_serial, key=terminal_serial.get)]
    return {"status": "recorded", "pending": pending, "log": log, "ready": not pending}


def alphabet():
    return [["begin", operation, key] for operation in range(2) for key in range(2)] + [
        ["finish", operation, key, outcome] for operation in range(2) for key in range(2)
        for outcome in production.OUTCOMES]


def all_words(max_length):
    commands = alphabet()
    for length in range(max_length + 1):
        for word in product(commands, repeat=length):
            yield list(word)


def invariants(result):
    if result["status"] == "rejected":
        equal(set(result), {"status", "index", "error"}, "rejection leaked snapshot")
        return
    pending, log = result["pending"], result["log"]
    pending_ids = [entry[0] for entry in pending]
    terminal_ids = [entry[0] for entry in log]
    equal(len(pending_ids), len(set(pending_ids)), "duplicate pending ID")
    equal(len(terminal_ids), len(set(terminal_ids)), "duplicate terminal ID")
    check(not set(pending_ids).intersection(terminal_ids), "pending/terminal ID overlap")
    equal(result["ready"], not pending, "global pending gate")
    check(all(entry[2] in production.OUTCOMES for entry in log), "unfinished terminal entry")


def finite_checks():
    counts = {"recorded": 0, "rejected": 0}
    checked = 0
    result_hash = hashlib.sha256()
    for word in all_words(4):
        actual = production.evaluate([TAG, word])
        equal(actual, oracle(word), "production vs independent lifecycle oracle")
        invariants(actual)
        counts[actual["status"]] += 1
        result_hash.update(digest(actual).encode())
        checked += 1
    scenarios = json.loads((ROOT / "examples/observation_recorder/scenarios.json").read_text())
    for scenario in scenarios:
        actual = production.evaluate([TAG, scenario["commands"]])
        equal(actual, oracle(scenario["commands"]), scenario["name"])
        equal(actual, scenario["expected"], "declared expectation: " + scenario["name"])
        invariants(actual)
    # Independence of the reducer's returned data from input state is observable.
    p, log = [[0, 0]], []
    p_before, log_before = deepcopy(p), deepcopy(log)
    following = production.step(p, log, ["finish", 0, 0, "success"])
    equal((p, log), (p_before, log_before), "step mutated arguments")
    following[1][0][1] = 99
    equal((p, log), (p_before, log_before), "step aliases arguments")
    return {"status": "passed", "alphabet_size": 16, "operation_ids": [0, 1],
        "keys": [0, 1], "word_lengths": [0, 4], "word_count": checked,
        "status_counts": counts, "result_sequence_sha256": result_hash.hexdigest(),
        "longer_scenarios": len(scenarios)}


def parser_checks():
    valid = [TAG, [["begin", 0, 0]]]
    invalid = [None, {}, [TAG], [TAG, [], "extra"], ["unknown", []], [TAG, {}],
        [TAG, [[]]], [TAG, [["begin", 0]]], [TAG, [["begin", 0, 0, 0]]],
        [TAG, [["begin", True, 0]]], [TAG, [["begin", 0, False]]],
        [TAG, [["begin", -1, 0]]], [TAG, [["begin", 0, 2**31]]],
        [TAG, [["finish", 0, 0, "unfinished"]]], [TAG, [["finish", 0, 0, None]]],
        [TAG, [["finish", 0, 0, 1]]], [TAG, [["unknown", 0, 0]]],
        [TAG, [{"command": "begin", "operation": 0, "key": 0}]],
        [TAG, [["begin", "0", 0]]]]
    for request in invalid:
        rejected(lambda request=request: production.evaluate(request))
    rejected(lambda: production.evaluate([TAG, [["begin", 0.0, 0]]]))
    raw_invalid = ["{\"x\":0,\"x\":1}", '["observation-recorder-v1",[["begin",0.0,0]]]',
        '["observation-recorder-v1",[["begin",0e0,0]]]',
        '["observation-recorder-v1",[["begin",NaN,0]]]',
        '["observation-recorder-v1",[["begin",Infinity,0]]]', "[", "null trailing"]
    for raw in raw_invalid:
        rejected(lambda raw=raw: production.loads_exact(raw))
    valid_boundary = [TAG, [["begin", 2**31 - 1, 2**31 - 1]]]
    production.evaluate(valid_boundary)
    command = ["begin", 0, 0]
    production.evaluate([TAG, [command] * 4096])
    production.evaluate([BATCH, [[]] * 256])
    production.evaluate([BATCH, [[command] * 4096] * 4])
    invalid_resource = [[TAG, [command] * 4097], [BATCH, [[]] * 257],
                        [BATCH, [[command] * 4096] * 4 + [[command]]]]
    for request in invalid_resource:
        rejected(lambda request=request: production.evaluate(request))
    # A malformed suffix invalidates the whole batch, even after a valid item.
    rejected(lambda: production.evaluate([BATCH, [valid[1], [["begin", True, 0]]]]))
    with tempfile.TemporaryDirectory(prefix="avoc-recorder-parser-") as directory:
        directory = Path(directory)
        path = directory / "request.json"
        path.write_text(json.dumps(valid))
        equal(production.load_exact(path), valid, "strict file loading")
        link = directory / "link.json"
        link.symlink_to(path)
        rejected(lambda: production.load_exact(link))
        rejected(lambda: production.load_exact(directory))
        path.write_bytes(b" " * (production.MAX_BYTES + 1))
        rejected(lambda: production.load_exact(path))
    return {"status": "passed", "invalid_structures": len(invalid) + 1,
        "invalid_raw_json": len(raw_invalid), "resource_rejections": len(invalid_resource),
        "boundary_acceptances": 4, "file_checks": 4,
        "invalid_requests_for_lean": invalid + invalid_resource,
        "valid_requests_for_lean": [valid_boundary, [TAG, [command] * 4096],
                                    [BATCH, [[]] * 256], [BATCH, [[command] * 4096] * 4]]}


def export_checks():
    registry_raw = json.loads((ROOT / "examples/observation_recorder/registry.json").read_text())
    registry = production.parse_registry(registry_raw)
    result = production.evaluate(production.load_exact(ROOT / "examples/observation_recorder/complete.json"))
    events = production.calibration_events(result, registry)
    selected = registry[0]
    authority = {"authority_id": "recorder-synthetic-fixture-v1", "total_alpha": "1/10",
        "grid": [0, "1/2", 1], "strata": [{"identity": protected,
            "checkpoints": [{"n": 1, "alpha": "1/50"}, {"n": 2, "alpha": "1/50"}]}
            for protected in registry.values()]}
    request = {"schema": "avoc-calibration-v1", "authority": authority,
        "selected_identity": selected, "checkpoint": 2, "events": events}
    calibrated = calibration.calibrate(request)
    equal((calibrated["n"], calibrated["successes"]), (2, 1), "terminal sample prefix counts")
    equal(calibrated["unresolved_intents"], [], "pending intent exported as immutable report")
    equal(calibrated["selected_stratum_status_counts"]["infrastructure_fault"], 1,
          "fault retained for accountability")
    equal(len(events), len(result["log"]), "one immutable event per completed ID")
    pending = production.evaluate(production.load_exact(ROOT / "examples/observation_recorder/pending.json"))
    rejected(lambda: production.calibration_events(pending, registry))
    rejected(lambda: production.calibration_events({"status": "rejected"}, registry))
    missing = dict(registry); missing.pop(1)
    rejected(lambda: production.calibration_events(result, missing))
    for mutation in ("duplicate_key", "duplicate_identity", "unknown_field", "bool_key"):
        bad = deepcopy(registry_raw)
        if mutation == "duplicate_key": bad["bindings"][1]["key"] = bad["bindings"][0]["key"]
        elif mutation == "duplicate_identity": bad["bindings"][1]["identity"] = bad["bindings"][0]["identity"]
        elif mutation == "unknown_field": bad["surprise"] = 1
        else: bad["bindings"][0]["key"] = False
        rejected(lambda bad=bad: production.parse_registry(bad))
    # The inherited immutable parser intentionally cannot finalize an old intent.
    legacy = deepcopy(request)
    intent = deepcopy(events[0]); intent["status"] = "intent"
    legacy["events"] = [intent, *events]
    rejected(lambda: calibration.calibrate(legacy))
    # Actual host CLI: pending export fails without producing a partial output.
    with tempfile.TemporaryDirectory(prefix="avoc-recorder-cli-") as directory:
        output = Path(directory) / "output.json"
        base = [sys.executable, str(ROOT / "tools/observation_recorder.py")]
        pending_run = subprocess.run(base + [str(ROOT / "examples/observation_recorder/pending.json"),
            "--registry", str(ROOT / "examples/observation_recorder/registry.json"),
            "--output", str(output)], capture_output=True, text=True, timeout=10)
        equal(pending_run.returncode, 2, "pending CLI export accepted")
        check(not output.exists(), "pending CLI export wrote partial result")
        complete_run = subprocess.run(base + [str(ROOT / "examples/observation_recorder/complete.json"),
            "--registry", str(ROOT / "examples/observation_recorder/registry.json"),
            "--output", str(output)], capture_output=True, text=True, timeout=10)
        equal(complete_run.returncode, 0, "complete CLI export failed")
        equal(json.loads(output.read_text())["calibration_events"], events, "actual CLI export")
    return {"status": "passed", "checks": 16, "terminal_events": len(events),
        "checked_prefix": {"n": calibrated["n"], "successes": calibrated["successes"]},
        "export_sha256": digest(events), "old_intent_then_terminal_rejected": True,
        "global_pending_blocks_export": True, "authentication_established": False}


def lean_checks(parser_results):
    from run_recorder_lean import run, runtime_provenance
    runtime_before = runtime_provenance()
    words = list(all_words(3))
    scenarios = json.loads((ROOT / "examples/observation_recorder/scenarios.json").read_text())
    words.extend(scenario["commands"] for scenario in scenarios)
    batches = []
    with tempfile.TemporaryDirectory(prefix="avoc-recorder-lean-") as directory:
        path = Path(directory) / "request.json"
        for start in range(0, len(words), production.MAX_BATCH):
            request = [BATCH, words[start:start + production.MAX_BATCH]]
            expected = production.evaluate(request)
            path.write_text(json.dumps(request))
            tick = time.monotonic()
            actual = run(path, 180)
            equal(actual, expected, "actual Lean/Python lifecycle disagreement")
            batches.append({"start": start, "count": len(request[1]),
                "request_sha256": digest(request), "response_sha256": digest(actual),
                "runtime_seconds": round(time.monotonic() - tick, 6)})
        # Structural invalidity probes invoke the actual Lean endpoint. Raw
        # lexical probes belong to the independent review (launcher rejects them).
        invalid_checks = 0
        for request in parser_results["invalid_requests_for_lean"]:
            path.write_text(json.dumps(request))
            rejected(lambda: run(path, 180))
            invalid_checks += 1
        for request in parser_results["valid_requests_for_lean"]:
            path.write_text(json.dumps(request))
            equal(run(path, 180), production.evaluate(request), "actual Lean resource boundary")
    equal(runtime_provenance(), runtime_before, "Lean executable/imported local objects changed during run")
    return {"status": "passed", "exhaustive_words": 4369, "word_lengths": [0, 3],
        "longer_scenarios": len(scenarios), "total_words": len(words), "batches": batches,
        "invalid_structure_checks": invalid_checks, "valid_boundary_checks": 4,
        "per_call_timeout_seconds": 180, "comparison": "exact parsed JSON equality",
        "runtime_provenance": runtime_before}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    sources = {path: sha(ROOT / path) for path in SOURCE_PATHS}
    finite = finite_checks()
    interface = parser_checks()
    export = export_checks()
    lean = lean_checks(interface) if args.lean else {"status": "not_run"}
    for field in ("invalid_requests_for_lean", "valid_requests_for_lean"):
        interface.pop(field)
    equal(sources, {path: sha(ROOT / path) for path in SOURCE_PATHS}, "source changed during execution")
    result = {"status": "passed", "started_at": started,
        "runtime_seconds": round(time.monotonic() - tick, 6),
        "python_version": platform.python_version(), "source_sha256": sources,
        "finite_oracle": finite, "interface": interface, "calibration_export": export,
        "actual_lean": lean, "non_claims": ["No universal Python/Lean refinement from finite tests",
            "No authentication, durable storage, real operation checking, or probability law validation",
            "No source-bit integrity established by the raw recorder commands"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "python_words": finite["word_count"],
        "lean_words": lean.get("total_words", 0), "runtime_seconds": result["runtime_seconds"]}))


if __name__ == "__main__":
    main()
