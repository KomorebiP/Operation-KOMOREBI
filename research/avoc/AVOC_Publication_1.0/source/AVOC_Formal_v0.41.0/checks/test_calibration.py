#!/usr/bin/env python3
"""Bounded independent exact calibration oracle and parser/replanning regression."""
from __future__ import annotations

from copy import deepcopy
import argparse
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
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import calibrate_quote as implementation


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: {actual!r} != {expected!r}")


def rejected(call, phrase):
    try:
        call()
    except implementation.CalibrationError as error:
        if phrase not in str(error):
            raise AssertionError(f"unexpected rejection: {error}") from error
        return
    raise AssertionError("invalid input was accepted: " + phrase)


def bernoulli_distribution(n, p):
    """Independent convolution: no binomial coefficient or interval evaluator."""
    distribution = [Fraction(1)]
    for _ in range(n):
        following = [Fraction(0)] * (len(distribution) + 1)
        for k, mass in enumerate(distribution):
            following[k] += mass * (1 - p)
            following[k + 1] += mass * p
        distribution = following
    return distribution


def sequence_distribution(n, p):
    """Second exact oracle, directly enumerating binary sequences for n <= 8."""
    distribution = [Fraction(0)] * (n + 1)
    for outcome in product((0, 1), repeat=n):
        mass = Fraction(1)
        for bit in outcome:
            mass *= p if bit else 1 - p
        distribution[sum(outcome)] += mass
    return distribution


def make_request(n=100, k=80, grid_size=100):
    plan = json.loads((ROOT / "examples/robust_quote/uncertain_plan.json").read_text())
    warm = plan[3][0]
    cold = plan[4][0]
    def encode(q):
        q = Fraction(q)
        return q.numerator if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    return {
        "schema": "avoc-calibration-v1",
        "authority": {"authority_id": f"fixed-demo-authority-grid{grid_size}-v1", "total_alpha": "1/20",
            "grid": [encode(Fraction(i, grid_size)) for i in range(grid_size + 1)],
            "strata": [
                {"identity": warm, "checkpoints": [{"n": 0, "alpha": "1/1000"},
                    {"n": 100, "alpha": "1/100"}, {"n": 500, "alpha": "1/100"}]},
                {"identity": cold, "checkpoints": [{"n": 100, "alpha": "1/100"}]}
            ]},
        "selected_identity": warm, "checkpoint": n,
        "events": [{"operation_id": f"warm-{i:04d}", "identity": warm,
                    "status": "checked_success" if i < k else "checked_rejection",
                    "evidence_id": f"checked-report-{i:04d}"} for i in range(n)]
    }


def mathematics_checks():
    cases = 0
    coverage_rows = []
    for n in range(13):
        for alpha in (Fraction(1, 20), Fraction(1, 5), Fraction(1, 2)):
            grid = [Fraction(i, 10) for i in range(11)]
            intervals = [implementation.interval(n, k, alpha, grid)[:2] for k in range(n + 1)]
            largest_miss = Fraction(0)
            largest_at = Fraction(0)
            for p in [Fraction(i, 40) for i in range(41)]:
                masses = bernoulli_distribution(n, p)
                assert_equal(sum(masses), Fraction(1), "binomial normalization")
                missed = Fraction(0)
                for k, (lower, upper) in enumerate(intervals):
                    excluded = not lower <= p <= upper
                    if excluded:
                        if masses[k] > alpha / (n + 1):
                            raise AssertionError("excluded a high-likelihood parameter")
                        missed += masses[k]
                    cases += 1
                if missed > alpha:
                    raise AssertionError("finite-sample miss probability exceeds allocated alpha")
                if missed > largest_miss:
                    largest_miss, largest_at = missed, p
            coverage_rows.append({"n": n, "alpha": implementation.wire(alpha),
                "maximum_miss_on_test_grid": implementation.wire(largest_miss),
                "maximizing_p": implementation.wire(largest_at)})
    sequence_checks = 0
    for n in range(9):
        for p in (Fraction(0), Fraction(1, 7), Fraction(1, 2), Fraction(6, 7), Fraction(1)):
            assert_equal(sequence_distribution(n, p), bernoulli_distribution(n, p),
                         "direct binary enumeration versus convolution")
            sequence_checks += 1
    # Exact hand cases, including zero data and both deterministic endpoints.
    assert_equal(implementation.interval(0, 0, Fraction(1, 20), [Fraction(0), Fraction(1)])[:2],
                 (Fraction(0), Fraction(1)), "no-data interval")
    for n in (1, 10, 100):
        grid = [Fraction(i, 100) for i in range(101)]
        assert_equal(implementation.interval(n, 0, Fraction(1, 20), grid)[0], Fraction(0), "all failures")
        assert_equal(implementation.interval(n, n, Fraction(1, 20), grid)[1], Fraction(1), "all successes")
    return {"count_mass_checks": cases, "independent_sequence_checks": sequence_checks,
            "coverage_grid": coverage_rows}


def interface_checks():
    base = make_request()
    result = implementation.calibrate(base)
    checks = []
    def passed(name):
        checks.append({"name": name, "status": "passed"})
    assert_equal((result["n"], result["successes"]), (100, 80), "sample counts")
    passed("checked successes and rejections counted")
    replay = deepcopy(base)
    replay["events"].append(deepcopy(replay["events"][0]))
    replay_result = implementation.calibrate(replay)
    assert_equal(replay_result["probability_band"], result["probability_band"], "duplicate interval")
    assert_equal(replay_result["duplicate_reports_ignored"], 1, "duplicate accounting")
    passed("identical operation replay idempotent")
    bad = deepcopy(replay)
    bad["events"][-1]["status"] = "checked_rejection"
    rejected(lambda: implementation.calibrate(bad), "conflicting replay")
    passed("conflicting replay rejected")
    fault = deepcopy(base)
    event = {"operation_id": "fault-1", "identity": base["selected_identity"],
             "status": "infrastructure_fault", "evidence_id": "timeout-report-1"}
    fault["events"].append(event)
    fault_result = implementation.calibrate(fault)
    assert_equal(fault_result["probability_band"], result["probability_band"], "fault exclusion")
    event2 = deepcopy(event)
    event2["status"] = "checked_rejection"
    fault["events"].append(event2)
    rejected(lambda: implementation.calibrate(fault), "conflicting replay")
    passed("fault excluded and cannot be relabeled as rejection")
    intent = deepcopy(base)
    intent["events"].append({"operation_id": "open-1", "identity": base["selected_identity"],
                             "status": "intent", "evidence_id": "unfinished-1"})
    intent_result = implementation.calibrate(intent)
    assert_equal(intent_result["probability_band"], result["probability_band"], "intent exclusion")
    plan = implementation.load_exact(ROOT / "examples/robust_quote/uncertain_plan.json")
    original = deepcopy(plan)
    rejected(lambda: implementation.replan_request(plan, intent_result), "unresolved intents")
    passed("unfinished intent excluded and replanning blocked")
    revised = implementation.replan_request(plan, result)
    assert_equal(plan, original, "old plan mutated")
    assert_equal(revised[4], original[4], "unselected cold quote mutated")
    assert_equal(revised[3][:3], original[3][:3], "deterministic selected quote changed")
    expected = [[implementation.rational(q, "bound").numerator,
                 implementation.rational(q, "bound").denominator] for q in result["probability_band"]]
    assert_equal(revised[3][3], expected, "new probability band")
    passed("fresh planning request preserves old plan and unselected quote")
    plan[3][3] = [[99, 100], [1, 1]]
    replaced = implementation.replan_request(plan, result)
    assert_equal(replaced[3][3], expected, "incorrect intersection with old band")
    passed("old probability band replaced without intersection")
    bad = deepcopy(base)
    bad["events"][0]["identity"] = deepcopy(bad["selected_identity"])
    bad["events"][0]["identity"][5] += "-changed"
    rejected(lambda: implementation.calibrate(bad), "absent from the authority")
    passed("mutated exact operation identity rejected")
    for field in (0, 3, 4, 5, 6, 7, 8):
        bad_plan = deepcopy(original)
        bad_plan[3][0][field] = ("cold" if field == 0 else 2 if field == 3 else "changed")
        rejected(lambda: implementation.replan_request(bad_plan, result), "exact calibrated identity")
    passed("plan identity mutations rejected")
    for value in (True, False, 0.5, "0.5", "2/4", "0/1", "1/1", "-0/2", "01/2", "1/0"):
        rejected(lambda value=value: implementation.rational(value, "probe"), "expected" if type(value) is not str or value in ("0.5", "01/2", "1/0") else "canonical")
    passed("boolean float and malformed or noncanonical fraction values rejected")
    rejected(lambda: implementation.interval(1, 1, 0.05, [Fraction(0), Fraction(1)]), "exact Fraction")
    passed("public arithmetic helper rejects approximate alpha")
    bad = deepcopy(base)
    bad["checkpoint"] = True
    rejected(lambda: implementation.calibrate(bad), "nonnegative integer")
    bad = deepcopy(base)
    bad["authority"]["strata"][0]["checkpoints"][0]["alpha"] = "1/2"
    rejected(lambda: implementation.calibrate(bad), "exceed the global")
    passed("global spending over identities and checkpoints enforced")
    bad = deepcopy(base)
    bad["checkpoint"] = 99
    rejected(lambda: implementation.calibrate(bad), "not predeclared")
    passed("undeclared stopping time rejected")
    bad = deepcopy(base)
    bad["events"].pop()
    rejected(lambda: implementation.calibrate(bad), "not enough checked")
    passed("insufficient checked sample rejected")
    bad = deepcopy(base)
    bad["authority"]["grid"][1] = 0
    rejected(lambda: implementation.calibrate(bad), "strictly increase")
    passed("invalid fixed grid rejected")
    # Extra later reports cannot change the old fixed checkpoint's data prefix.
    extra = deepcopy(base)
    extra["events"].append({"operation_id": "later-1", "identity": base["selected_identity"],
                            "status": "checked_rejection", "evidence_id": "later-checked"})
    assert_equal(implementation.calibrate(extra)["probability_band"], result["probability_band"], "checkpoint prefix")
    passed("checkpoint uses first n unique checked reports")
    cold = deepcopy(base)
    cold["events"].append({"operation_id": "cold-1", "identity": base["authority"]["strata"][1]["identity"],
                           "status": "checked_rejection", "evidence_id": "cold-checked"})
    assert_equal(implementation.calibrate(cold)["probability_band"], result["probability_band"], "identity stratification")
    passed("other identity does not contaminate calibration sample")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "request.json"
        for raw, phrase in (("{\"x\":1,\"x\":2}", "duplicate JSON key"),
                            ("{\"x\":0.5}", "floating/nonfinite"),
                            ("{\"x\":NaN}", "floating/nonfinite")):
            path.write_text(raw)
            rejected(lambda: implementation.load_exact(path), phrase)
    passed("JSON duplicate keys floats and nonfinite values rejected")
    return checks


def lean_crosscheck():
    """Compare actual Lean endpoints without using them inside either oracle."""
    from run_calibration_lean import run
    requests = []
    for n in range(9):
        for k in range(n + 1):
            for cells in (5, 10):
                for alpha in ("1/20", "1/5"):
                    requests.append(["calibration-binomial-v1", n, k, cells, alpha])
    requests += [["calibration-binomial-v1", n, k, 100, "1/100"]
                 for n, k in ((0, 0), (100, 80), (500, 400))]
    requests.append(["calibration-binomial-v1", 500, 400, 1000, "1/100"])
    with tempfile.TemporaryDirectory(prefix="calibration-crosscheck-") as directory:
        path = Path(directory) / "batch.json"
        path.write_text(json.dumps(["calibration-batch-v1", requests]))
        actual = run(path)
    if actual.get("status") != "calibration_batch" or len(actual.get("results", [])) != len(requests):
        raise AssertionError("Lean batch response shape mismatch")
    for request, response in zip(requests, actual["results"]):
        if response.get("ok") is not True:
            raise AssertionError(f"Lean rejected valid request: {request}: {response}")
        _, n, k, m, alpha_text = request
        alpha = Fraction(alpha_text)
        lower, upper, _ = implementation.interval(n, k, alpha, [Fraction(i, m) for i in range(m + 1)])
        value = response["value"]
        assert_equal((Fraction(value["lower"]), Fraction(value["upper"])), (lower, upper), "Lean interval")
        assert_equal(Fraction(value["threshold"]), alpha / (n + 1), "Lean threshold")
        assert_equal((value["n"], value["k"], value["grid_cells"]), (n, k, m), "Lean metadata")
    record = {"status": "passed", "comparisons": len(requests),
              "requests": requests, "actual_lean_output": actual,
              "boundary": "Executed finite equality checks, not universal Python/Lean refinement."}
    path = ROOT / "results/v0.39.0/calibration_lean_crosscheck.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return {"status": "passed", "comparisons": len(requests), "output": str(path.relative_to(ROOT))}


def lean_replanning_check():
    from run_robust_quote import run
    plan = ROOT / "examples/robust_quote/uncertain_plan.json"
    sample = ROOT / "examples/calibration/n500_k400_grid1000.json"
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (plan, sample)}
    old = run(plan)
    output = ROOT / "results/v0.39.0/calibration_lean_replan_n500_grid1000.json"
    command = [sys.executable, str(ROOT / "tools/calibrate_quote.py"), str(sample),
               "--plan", str(plan), "--output", str(output)]
    completed = subprocess.run(command, text=True, capture_output=True, timeout=300, cwd=ROOT)
    if completed.returncode:
        raise AssertionError("actual calibration/planning CLI failed: " + completed.stderr)
    new = json.loads(output.read_text())
    assert_equal(old["robust_choice"], "generate_cold", "old robust choice")
    assert_equal(new["lean_plan"]["robust_choice"], "inspect_warm", "recalibrated robust choice")
    assert_equal(new["lean_calibration"]["status"], "calibrated", "actual Lean calibration")
    warm = next(action for action in new["lean_plan"]["actions"] if action["action"] == "inspect_warm")
    if Fraction(warm["radius"]) <= 0:
        raise AssertionError("dominance scenario must have a nonzero warm radius")
    corrected = next(action for action in new["competitor_dominance"] if action["action"] == "inspect_warm")
    assert_equal(corrected["certified_dominance"], True, "corrected competitor dominance")
    for path, digest in before.items():
        assert_equal(hashlib.sha256(path.read_bytes()).hexdigest(), digest, "input mutated")
    return {"status": "passed", "original_action": old["robust_choice"],
            "calibrated_action": new["lean_plan"]["robust_choice"],
            "band": new["probability_band"], "output": str(output.relative_to(ROOT)),
            "warm_radius": warm["radius"], "corrected_dominance": True,
            "boundary": "Synthetic fixed-authority sample; new episode; no operation was executed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", action="store_true", help="also compare actual pinned Lean endpoint")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    result = {"status": "passed", "mathematics": mathematics_checks(),
              "interface": interface_checks(), "non_claims": [
                  "Finite p-grid regression is not a universal coverage proof.",
                  "No proof of empirical IID, stationarity, log completeness, noninformative fault selection or authority authentication.",
                  "No universal Python-to-Lean implementation refinement."]}
    examples = ROOT / "examples/calibration"
    examples.mkdir(parents=True, exist_ok=True)
    scenario_results = []
    for n, k, cells in ((0, 0, 100), (100, 80, 100), (500, 400, 100), (500, 400, 1000)):
        request = make_request(n, k, grid_size=cells)
        name = f"n{n}_k{k}" + (f"_grid{cells}" if cells != 100 else "")
        path = examples / f"{name}.json"
        path.write_text(json.dumps(request, indent=2) + "\n")
        output = implementation.calibrate(request)
        (ROOT / f"results/v0.39.0/calibration_{name}.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
        lo, hi = [implementation.rational(x, "bound") for x in output["probability_band"]]
        if n and not (0 < lo < Fraction(k, n) < hi < 1):
            raise AssertionError("nontrivial large-sample example failed")
        scenario_results.append({"n": n, "k": k, "grid_cells": cells, "band": output["probability_band"]})
    result["examples"] = scenario_results
    if args.lean:
        result["lean_crosscheck"] = lean_crosscheck()
        result["lean_replanning"] = lean_replanning_check()
    result["runtime_seconds"] = round(time.monotonic() - clock, 6)
    result["started_at"] = started
    result["python"] = platform.python_version()
    result["source_sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (ROOT / "tools/calibrate_quote.py", Path(__file__))}
    output = ROOT / "results/v0.39.0/calibration_regression.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "count_mass_checks": result["mathematics"]["count_mass_checks"],
                      "independent_sequence_checks": result["mathematics"]["independent_sequence_checks"],
                      "interface_checks": len(result["interface"]), "examples": scenario_results,
                      "output": str(output)}))


if __name__ == "__main__":
    main()
