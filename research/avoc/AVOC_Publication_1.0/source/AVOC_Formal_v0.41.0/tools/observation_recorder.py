#!/usr/bin/env python3
"""Pure exact snapshot recorder for AVOC operation intents and terminal reports.

No operation is executed, retried, authenticated, or certified by this program.
Each request starts empty; pending operations and immutable terminal reports are
separate. A registry export is a syntactic adapter, not a sampling-law proof.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

MAX_BYTES = 4_194_304
MAX_COMMANDS = 4096
MAX_BATCH = 256
MAX_BATCH_COMMANDS = 16384
MAX_NAT = 2**31 - 1
OUTCOMES = ("success", "rejection", "fault")


class RecorderError(ValueError):
    pass


def fail(message):
    raise RecorderError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate JSON field: " + key)
        result[key] = value
    return result


def reject_number(token):
    fail("decimal, exponent, and nonfinite numbers are forbidden: " + token)


def loads_exact(text):
    if len(text.encode("utf-8")) > MAX_BYTES:
        fail("input exceeds 4 MiB")
    try:
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_float=reject_number, parse_constant=reject_number)
    except (json.JSONDecodeError, RecursionError) as error:
        fail("invalid JSON: " + str(error))


def load_exact(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        fail("input must be a regular nonsymlink file of at most 4 MiB")
    return loads_exact(path.read_text(encoding="utf-8"))


def nat(value):
    if type(value) is not int or not 0 <= value <= MAX_NAT:
        fail("ID and key must be integers in [0, 2147483647]")
    return value


def validate_commands(commands):
    if type(commands) is not list or len(commands) > MAX_COMMANDS:
        fail("commands must be an array of at most 4096 entries")
    for command in commands:
        if type(command) is not list or not command or type(command[0]) is not str:
            fail("command must be an array starting with begin or finish")
        if command[0] == "begin" and len(command) == 3:
            nat(command[1]); nat(command[2])
        elif command[0] == "finish" and len(command) == 4:
            nat(command[1]); nat(command[2])
            if type(command[3]) is not str or command[3] not in OUTCOMES:
                fail("terminal outcome must be success, rejection, or fault")
        else:
            fail("unknown command or wrong command arity")


def step(pending, log, command):
    """Return a fresh (pending, log), or None. Inputs are never mutated."""
    kind, operation, key = command[:3]
    completed = next((event for event in log if event[0] == operation), None)
    intent = next((entry for entry in pending if entry[0] == operation), None)
    if kind == "begin":
        if completed is not None:
            return (deepcopy(pending), deepcopy(log)) if completed[1] == key else None
        if intent is not None:
            return (deepcopy(pending), deepcopy(log)) if intent[1] == key else None
        return deepcopy(pending) + [[operation, key]], deepcopy(log)
    event = [operation, key, command[3]]
    if completed is not None:
        return (deepcopy(pending), deepcopy(log)) if completed == event else None
    if intent != [operation, key]:
        return None
    return [entry[:] for entry in pending if entry[0] != operation], deepcopy(log) + [event]


def reduce_commands(commands):
    """Evaluate a validated finite command word from the empty state."""
    pending, log = [], []
    for index, command in enumerate(commands):
        following = step(pending, log, command)
        if following is None:
            return {"status": "rejected", "index": index, "error": "command_rejected"}
        pending, log = following
    return {"status": "recorded", "pending": pending, "log": log, "ready": not pending}


def evaluate(request):
    if type(request) is not list or len(request) != 2 or type(request[0]) is not str:
        fail("expected a two-element tagged request array")
    tag, body = request
    if tag == "observation-recorder-v1":
        validate_commands(body)
        return reduce_commands(body)
    if tag != "observation-recorder-batch-v1":
        fail("unknown recorder schema")
    if type(body) is not list or len(body) > MAX_BATCH:
        fail("batch must be an array of at most 256 command arrays")
    total = 0
    # Validate the entire request before exposing any result.
    for commands in body:
        validate_commands(commands)
        total += len(commands)
        if total > MAX_BATCH_COMMANDS:
            fail("batch exceeds 16384 commands")
    return {"status": "recorder_batch", "results": [reduce_commands(word) for word in body]}


def parse_registry(raw):
    """Require an injective explicit map from Nat keys to protected identities."""
    import calibrate_quote
    if type(raw) is not dict or set(raw) != {"schema", "bindings"}:
        fail("registry requires exactly schema and bindings")
    if raw["schema"] != "observation-recorder-registry-v1":
        fail("unknown registry schema")
    bindings = raw["bindings"]
    if type(bindings) is not list or not 1 <= len(bindings) <= 100:
        fail("registry must contain between one and 100 bindings")
    result, identities = {}, set()
    for binding in bindings:
        if type(binding) is not dict or set(binding) != {"key", "identity"}:
            fail("registry binding requires exactly key and identity")
        key = nat(binding["key"])
        protected = calibrate_quote.identity(binding["identity"])
        identity_key = calibrate_quote.canonical(protected)
        if key in result or identity_key in identities:
            fail("registry keys and protected identities must both be unique")
        result[key] = protected
        identities.add(identity_key)
    return result


def calibration_events(result, registry):
    """Export a complete ready snapshot for the existing calibration parser.

    The evidence_id values below identify recorder terminal records only. They
    are not signatures, checker certificates, or evidence of a real operation.
    """
    if result.get("status") != "recorded" or result.get("ready") is not True or result.get("pending"):
        fail("calibration export requires an accepted snapshot with no pending operations")
    status = {"success": "checked_success", "rejection": "checked_rejection",
              "fault": "infrastructure_fault"}
    events = []
    for operation, key, outcome in result["log"]:
        if key not in registry:
            fail("terminal event key is absent from the explicit registry")
        events.append({"operation_id": "recorder-" + str(operation),
            "identity": deepcopy(registry[key]), "status": status[outcome],
            "evidence_id": "recorder-terminal-" + str(operation)})
    return events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--registry", type=Path,
                        help="attach calibration_events; requires a ready single snapshot")
    args = parser.parse_args()
    try:
        result = evaluate(load_exact(args.request))
        if args.registry:
            registry = parse_registry(load_exact(args.registry))
            result["calibration_events"] = calibration_events(result, registry)
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            if args.output.is_symlink():
                fail("symlink output rejected")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except Exception as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
