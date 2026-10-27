#!/usr/bin/env python3
"""Exact finite-checkpoint probability calibration from protected operation logs.

This parser does not authenticate its input or prove the IID/selection model.
The supplied authority must have been fixed before observing the sample. See
examples/calibration/README.md for the statistical and runtime boundaries.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_N = 2000
MAX_GRID = 1001
MAX_EVENTS = 20000
STATUSES = {"checked_success", "checked_rejection", "infrastructure_fault", "intent"}
RATIONALE = ("Fixed predeclared checkpoints and identity strata; independent identically "
             "distributed checked binary outcomes with fixed within-stratum probability; "
             "noninformative exclusion of faults and unfinished operations; authenticated "
             "complete log and authority are supplied assumptions, not parser conclusions.")


class CalibrationError(ValueError):
    pass


def fail(message):
    raise CalibrationError(message)


def strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            fail(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def reject_number(text):
    fail(f"floating/nonfinite JSON numbers are forbidden: {text}")


def load_exact(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
        fail("request must be a regular nonsymlink file of at most 32 MiB")
    return json.loads(path.read_text(), object_pairs_hook=strict_object,
                      parse_float=reject_number, parse_constant=reject_number)


def fields(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        fail(f"{label}: expected exactly {sorted(expected)}")


def nat(value, label, maximum=None):
    if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
        fail(f"{label}: expected a nonnegative integer within the resource bound")
    return value


def identifier(value, label):
    if type(value) is not str or not value or len(value) > 256:
        fail(f"{label}: expected a nonempty string of at most 256 characters")
    return value


def rational(value, label):
    if type(value) is int:
        return Fraction(value)
    if type(value) is not str or len(value) > 1024 or not re.fullmatch(r"-?(?:0|[1-9][0-9]*)/[1-9][0-9]*", value):
        fail(f"{label}: expected an integer or canonical reduced rational string")
    answer = Fraction(value)
    if value != f"{answer.numerator}/{answer.denominator}" or answer.denominator == 1:
        fail(f"{label}: rational string must be reduced, nonintegral and canonical")
    return answer


def wire(value):
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identity(value):
    """The exact decoded v0.38 F5 quote identity; no hash equality is trusted."""
    if not isinstance(value, list) or len(value) != 9:
        fail("identity: expected the nine-field v0.38 quote identity")
    if value[0] not in ("warm", "cold"):
        fail("identity: operation kind must be warm or cold")
    matrix, offset = value[1:3]
    if not isinstance(matrix, list) or not matrix or len(matrix) > 64:
        fail("identity: invalid source matrix")
    width = len(matrix[0]) if isinstance(matrix[0], list) else 0
    if not 0 < width <= 64:
        fail("identity: invalid source width")
    for row in matrix:
        if not isinstance(row, list) or len(row) != width:
            fail("identity: ragged source matrix")
        for entry in row:
            nat(entry, "F5 source entry", 4)
    if not isinstance(offset, list) or len(offset) != len(matrix):
        fail("identity: invalid source offset")
    for entry in offset:
        nat(entry, "F5 offset entry", 4)
    nat(value[3], "deployment-call count")
    for field in value[4:]:
        identifier(field, "identity field")
    return deepcopy(value)


def parse_authority(raw):
    fields(raw, {"authority_id", "total_alpha", "grid", "strata"}, "authority")
    identifier(raw["authority_id"], "authority_id")
    total = rational(raw["total_alpha"], "total_alpha")
    if not 0 < total < 1:
        fail("total_alpha must lie strictly between zero and one")
    if not isinstance(raw["grid"], list) or not 2 <= len(raw["grid"]) <= MAX_GRID:
        fail("grid length is outside resource bounds")
    grid = [rational(x, "grid point") for x in raw["grid"]]
    if grid[0] != 0 or grid[-1] != 1 or any(a >= b for a, b in zip(grid, grid[1:])):
        fail("grid must strictly increase from zero to one")
    if any(point != Fraction(i, len(grid) - 1) for i, point in enumerate(grid)):
        fail("grid must be uniform to match the checked Lean calibration function")
    if not isinstance(raw["strata"], list) or not 1 <= len(raw["strata"]) <= 100:
        fail("authority needs between one and 100 identity strata")
    allocated = Fraction(0)
    strata = {}
    for stratum in raw["strata"]:
        fields(stratum, {"identity", "checkpoints"}, "stratum")
        key = canonical(identity(stratum["identity"]))
        if key in strata:
            fail("duplicate identity stratum")
        if not isinstance(stratum["checkpoints"], list) or not 1 <= len(stratum["checkpoints"]) <= 100:
            fail("stratum needs between one and 100 fixed checkpoints")
        schedule = {}
        previous = -1
        for point in stratum["checkpoints"]:
            fields(point, {"n", "alpha"}, "checkpoint")
            n = nat(point["n"], "checkpoint n", MAX_N)
            alpha = rational(point["alpha"], "checkpoint alpha")
            if n <= previous or not 0 < alpha < 1:
                fail("checkpoints must strictly increase and have alpha in (0,1)")
            previous = n
            schedule[n] = alpha
            allocated += alpha
        strata[key] = schedule
    if allocated > total:
        fail("checkpoint alpha allocations exceed the global error budget")
    return grid, strata, allocated, total


def interval(n, k, alpha, grid):
    """Conservative grid hull; all arithmetic is exact Fraction/integer arithmetic."""
    nat(n, "sample size", MAX_N)
    nat(k, "success count", n)
    if type(alpha) is not Fraction or any(type(point) is not Fraction for point in grid):
        fail("calibration arithmetic requires exact Fraction inputs")
    if not 0 < alpha < 1:
        fail("alpha must lie in (0,1)")
    if not grid or grid[0] != 0 or grid[-1] != 1 or any(a >= b for a, b in zip(grid, grid[1:])):
        fail("invalid grid")
    if any(point != Fraction(i, len(grid) - 1) for i, point in enumerate(grid)):
        fail("grid must be uniform")
    if n == 0:
        return Fraction(0), Fraction(1), list(range(len(grid) - 1))
    threshold = alpha / (n + 1)
    retained = [i for i, (lower, upper) in enumerate(zip(grid, grid[1:]))
                if comb(n, k) * upper ** k * (1 - lower) ** (n - k) > threshold]
    if not retained:
        return Fraction(0), Fraction(1), []
    return grid[retained[0]], grid[retained[-1] + 1], retained


def calibrate(request):
    fields(request, {"schema", "authority", "selected_identity", "checkpoint", "events"}, "request")
    if request["schema"] != "avoc-calibration-v1":
        fail("unknown calibration schema")
    grid, strata, allocated, total = parse_authority(request["authority"])
    selected = identity(request["selected_identity"])
    selected_key = canonical(selected)
    n = nat(request["checkpoint"], "checkpoint", MAX_N)
    if selected_key not in strata or n not in strata[selected_key]:
        fail("selected identity/checkpoint was not predeclared by the supplied authority")
    if not isinstance(request["events"], list) or len(request["events"]) > MAX_EVENTS:
        fail("event list exceeds resource bound")
    seen = {}
    duplicate_count = 0
    outcomes = []
    counts = {status: 0 for status in sorted(STATUSES)}
    unresolved = []
    for event in request["events"]:
        fields(event, {"operation_id", "identity", "status", "evidence_id"}, "operation event")
        op = identifier(event["operation_id"], "operation_id")
        event_key = canonical(identity(event["identity"]))
        if event_key not in strata:
            fail("operation identity is absent from the authority strata")
        if type(event["status"]) is not str or event["status"] not in STATUSES:
            fail("unknown operation status")
        identifier(event["evidence_id"], "evidence_id")
        if op in seen:
            if seen[op] != event:
                fail("conflicting replay for operation_id " + op)
            duplicate_count += 1
            continue
        seen[op] = deepcopy(event)
        if event["status"] == "intent":
            unresolved.append(op)
        if event_key == selected_key:
            counts[event["status"]] += 1
            if event["status"] in ("checked_success", "checked_rejection"):
                outcomes.append(event["status"] == "checked_success")
    if len(outcomes) < n:
        fail("not enough checked binary outcomes for the requested checkpoint")
    # A checkpoint always uses the first n unique checked reports in log order.
    k = sum(outcomes[:n])
    alpha = strata[selected_key][n]
    lower, upper, retained = interval(n, k, alpha, grid)
    return {
        "schema": "avoc-calibration-result-v1", "status": "calibrated",
        "identity": selected, "n": n, "successes": k,
        "alpha": wire(alpha), "threshold": wire(alpha / (n + 1)),
        "probability_band": [wire(lower), wire(upper)],
        "retained_cells": retained, "grid_cells": len(grid) - 1,
        "selected_stratum_status_counts": counts, "duplicate_reports_ignored": duplicate_count,
        "checked_reports_beyond_checkpoint": len(outcomes) - n,
        "unresolved_intents": unresolved, "replanning_allowed": not unresolved,
        "provenance": {"authority": deepcopy(request["authority"]),
                       "authority_sha256": fingerprint(request["authority"]),
                       "request_sha256": fingerprint(request),
                       "global_alpha": wire(total), "allocated_alpha": wire(allocated),
                       "interval_rule": "binomial-cell-envelope-hull-v1",
                       "prior_band_policy": "replace; never intersect automatically"},
        "supplied_assumptions": RATIONALE,
        "authentication_status": "caller-supplied protected inputs; no cryptographic authentication performed",
    }


def replan_request(plan, result):
    if result["unresolved_intents"]:
        fail("replanning blocked: unresolved intents retain their original quote evidence")
    if not isinstance(plan, list) or len(plan) != 7 or plan[0] != "robust-quote-plan-f5-v1":
        fail("expected a v0.38 robust-quote-plan-f5-v1 request")
    selected = result["identity"]
    slot = 3 if selected[0] == "warm" else 4
    quote = plan[slot]
    if not isinstance(quote, list) or len(quote) != 4 or identity(quote[0]) != selected:
        fail("planning quote does not match the exact calibrated identity")
    calls = nat(plan[2], "planning deployment-call count")
    if calls != selected[3]:
        fail("planning workload differs from calibrated identity")
    source = plan[1]
    if (not isinstance(source, list) or len(source) != 5 or source[0] != "map"
            or source[1] != len(selected[1]) or source[2] != len(selected[1][0])
            or source[3] != selected[1] or source[4] != selected[2]):
        fail("planning source differs from calibrated identity")
    nat(source[1], "planning source rows", 64)
    nat(source[2], "planning source columns", 64)
    identity([selected[0], source[3], source[4], *selected[3:]])
    # The Lean codec performs full request validation. We preserve all other
    # fields and return a new value, never modifying an in-flight plan or file.
    revised = deepcopy(plan)
    revised[slot][3] = [[rational(x, "probability bound").numerator,
                          rational(x, "probability bound").denominator]
                         for x in result["probability_band"]]
    return revised


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--plan", type=Path, help="replan by invoking the actual inherited Lean endpoint")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    try:
        nat(args.timeout, "timeout", 300)
        if args.timeout == 0:
            fail("timeout must be positive")
        request = load_exact(args.request)
        result = calibrate(request)
        if args.plan:
            import tempfile
            from run_calibration_lean import run as run_calibration
            original = load_exact(args.plan)
            # Reject in-flight state and exact identity mismatch before invoking
            # either Lean endpoint. This does not modify the original request.
            replan_request(original, result)
            with tempfile.TemporaryDirectory(prefix="avoc-calibration-") as directory:
                calibration_path = Path(directory) / "calibration.json"
                calibration_path.write_text(json.dumps([
                    "calibration-binomial-v1", result["n"], result["successes"],
                    result["grid_cells"], result["alpha"]]))
                checked = run_calibration(calibration_path, args.timeout)
                if checked.get("status") != "calibrated":
                    fail("Lean calibration returned an unexpected status")
                checked_band = [wire(Fraction(checked["lower"])), wire(Fraction(checked["upper"]))]
                if checked_band != result["probability_band"]:
                    fail("Lean/Python calibration disagreement")
                if (checked["n"], checked["k"], checked["grid_cells"]) != (
                        result["n"], result["successes"], result["grid_cells"]):
                    fail("Lean calibration metadata disagreement")
                if (Fraction(checked["alpha"]) != rational(result["alpha"], "alpha")
                        or Fraction(checked["threshold"]) != rational(result["threshold"], "threshold")):
                    fail("Lean calibration threshold disagreement")
                result["lean_calibration"] = checked
                result["probability_band"] = checked_band
                revised = replan_request(original, result)
                path = Path(directory) / "new_plan.json"
                planning_request = ["calibrated-quote-plan-f5-v1", *revised[1:]]
                path.write_text(json.dumps(planning_request))
                planning = run_calibration(path, args.timeout)
                if planning.get("status") != "calibrated_quote_plan":
                    fail("Lean calibrated planner returned an unexpected status")
                result["lean_plan"] = planning["plan"]
                result["competitor_dominance"] = planning["competitor_dominance"]
                result["lean_planning_endpoint"] = "calibrated-quote-plan-f5-v1"
            slot = 3 if result["identity"][0] == "warm" else 4
            result["replanned_request"] = revised
            result["replaced_probability_band"] = original[slot][3]
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        else:
            print(rendered, end="")
        return 0
    except Exception as error:
        print(json.dumps({"status": "calibration_error", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
