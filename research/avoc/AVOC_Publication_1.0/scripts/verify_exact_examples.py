#!/usr/bin/env python3
"""Exact, bounded publication examples. Never edits the inherited release."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from math import comb
from pathlib import Path
import platform
import sys
import time

sys.dont_write_bytecode = True
PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "source/AVOC_Formal_v0.41.0"
sys.path.insert(0, str(SOURCE / "tools"))
import calibrate_quote as calibration
import observation_recorder as recorder


def wire(q):
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    return {str(path.relative_to(SOURCE)): sha(path)
            for path in sorted(SOURCE.rglob("*")) if path.is_file()}


def independent_grid_interval(n, k, cells, alpha):
    # Integer-only cross multiplication of the cell rule, independent of the
    # Fraction evaluator in the inherited implementation.
    threshold = alpha.numerator * cells ** n
    multiplier = (n + 1) * alpha.denominator * comb(n, k)
    kept = [i for i in range(cells)
            if multiplier * (i + 1) ** k * (cells - i) ** (n - k) > threshold]
    return (F(kept[0], cells), F(kept[-1] + 1, cells), kept) if kept else (F(0), F(1), [])


def completed_reports(bits):
    order = sorted(range(len(bits)), key=lambda i: (not bits[i], i))
    commands = [["begin", i, 0] for i in range(len(bits))]
    commands += [["finish", i, 0, "success" if bits[i] else "rejection"] for i in order]
    result = recorder.evaluate(["observation-recorder-v1", commands])
    assert result["status"] == "recorded" and result["ready"] and result["pending"] == []
    reports = [event[2] == "success" for event in result["log"]]
    assert len(reports) == len(bits) and sum(reports) == sum(bits)
    return order, reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    before = source_hashes()
    calibration_tests = load_module("avoc_calibration_tests", SOURCE / "checks/test_calibration.py")
    mathematical = calibration_tests.mathematics_checks()
    interface = calibration_tests.interface_checks()
    grid_cases = []
    for n, k, cells, alpha in [(0, 0, 10, F(1, 20)), (10, 10, 10, F(1, 10)),
                               (100, 80, 100, F(1, 100)), (500, 400, 1000, F(1, 100))]:
        observed = calibration.interval(n, k, alpha, [F(i, cells) for i in range(cells + 1)])
        if n:
            assert observed == independent_grid_interval(n, k, cells, alpha)
        else:
            assert observed[:2] == (F(0), F(1))
        grid_cases.append({"n": n, "k": k, "cells": cells, "alpha": wire(alpha),
                           "interval": list(map(wire, observed[:2])), "retained_cells": observed[2]})
    assert grid_cases[-1]["interval"] == ["361/500", "433/500"]
    fixture = calibration.calibrate(calibration.load_exact(SOURCE / "examples/calibration/n500_k400_grid1000.json"))
    assert fixture["probability_band"] == ["361/500", "433/500"]

    four_cases = []
    for bits in product([False, True], repeat=2):
        order, reports = completed_reports(bits)
        four_cases.append({"attempt_bits": list(bits), "completion_order": order,
                           "reported_bits": reports, "mass": "1/4"})
    first_mass = sum((F(1, 4) for row in four_cases if row["reported_bits"][0]), F(0))
    assert first_mass == F(3, 4)
    twenty = []
    for total in range(21):
        order, reports = completed_reports([True] * total + [False] * (20 - total))
        k = sum(reports[:10])
        assert k == min(total, 10)
        lo, hi, _ = calibration.interval(10, k, F(1, 10), [F(i, 10) for i in range(11)])
        mass = F(comb(20, total), 2 ** 20)
        twenty.append({"attempt_successes": total, "first_ten_successes": k,
                       "multiplicity": comb(20, total), "mass": wire(mass),
                       "interval": [wire(lo), wire(hi)], "misses_half": not lo <= F(1, 2) <= hi,
                       "lower_bound_event": total >= 10})
    lower_bound = sum((F(row["mass"]) for row in twenty if row["lower_bound_event"]), F(0))
    exact_miss = sum((F(row["mass"]) for row in twenty if row["misses_half"]), F(0))
    assert lower_bound == F(308333, 524288) and lower_bound > F(1, 10)
    assert sum(row["multiplicity"] for row in twenty) == 2 ** 20
    assert twenty[10]["interval"] == ["3/5", "1"]

    # Two fair source bits, second available iff first is true. Availability
    # depends only on past outcomes; conditioning on completion still biases.
    deadline = [{"bits": list(bits), "complete": bits[0], "mass": "1/4"}
                for bits in product([False, True], repeat=2)]
    completion_mass = sum((F(1, 4) for row in deadline if row["complete"]), F(0))
    conditional_first = sum((F(1, 4) for row in deadline if row["complete"] and row["bits"][0]), F(0)) / completion_mass
    assert completion_mass == F(1, 2) and conditional_first == 1
    censor_p, retain_success, retain_failure = F(1, 2), F(1), F(0)
    conditional_retained = censor_p * retain_success / (censor_p * retain_success + (1 - censor_p) * retain_failure)
    assert conditional_retained == 1

    gross, warm_fee, cold_fee = F(15000), F(133), F(196)
    crossing = (gross - cold_fee + warm_fee) / gross
    assert crossing == F(4979, 5000)
    assert crossing * gross - warm_fee == gross - cold_fee == 14804
    assert gross - warm_fee == 14867
    lo, hi = map(F, fixture["probability_band"])
    reward_envelope = F(260)
    warm_nominal = lo * 200
    warm_radius = 2 * (hi - lo) * reward_envelope
    warm_lower, warm_upper = warm_nominal - warm_radius, warm_nominal + warm_radius
    assert (warm_nominal, warm_radius, warm_lower, warm_upper) == (F(722, 5), F(1872, 25), F(1738, 25), F(5482, 25))
    assert warm_lower > 60 and warm_lower > 0
    old_nominal, old_radius = F(3, 5) * 200, 2 * F(2, 5) * reward_envelope
    assert (old_nominal, old_radius, old_nominal - old_radius) == (120, 208, -88)

    replay_word = [["begin", 0, 0], ["finish", 0, 0, "success"],
                   ["finish", 0, 0, "success"], ["begin", 0, 0]]
    replay_prefixes = [recorder.evaluate(["observation-recorder-v1", replay_word[:i]]) for i in range(5)]
    assert [len(result["log"]) for result in replay_prefixes] == [0, 0, 1, 1, 1]
    changed = recorder.evaluate(["observation-recorder-v1", replay_word + [["finish", 0, 0, "rejection"]]])
    assert changed == {"status": "rejected", "index": 4, "error": "command_rejected"}
    after = source_hashes()
    assert before == after, "Inherited release files changed"

    result = {
        "status": "passed", "evidence_kind": "Exact finite rational computation and bounded Python regression",
        "started_at": started, "runtime_seconds": round(time.monotonic() - tick, 6),
        "python": platform.python_version(), "release_files_checked_unchanged": len(before),
        "source_tree_digest": hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
        "calibration_regression": {"count_mass_checks": mathematical["count_mass_checks"],
            "independent_sequence_checks": mathematical["independent_sequence_checks"],
            "interface_checks": len(interface), "interface": interface,
            "bounds": {"n": [0, 12], "alpha": ["1/20", "1/5", "1/2"], "grid_cells": 10,
                "p_grid": "i/40 for 0<=i<=40", "sequence_oracle": "n=0..8; p in {0,1/7,1/2,6/7,1}"}},
        "grid_cases": grid_cases,
        "rank_one": {"baseline_cost": 36, "selected_cost": 21, "calls": 1000, "gross": wire(gross),
                     "warm_fee": wire(warm_fee), "cold_fee": wire(cold_fee), "warm_net": "14867",
                     "cold_net": "14804", "crossing_warm_probability": wire(crossing)},
        "robust_original": {"warm_nominal": wire(old_nominal), "warm_radius": wire(old_radius),
            "warm_interval": ["-88", "328"], "cold_interval": ["60", "60"], "stop_interval": ["0", "0"],
            "robust_choice": "generate_cold", "nominal_choice": "inspect_warm"},
        "robust_calibrated": {"warm_nominal": wire(warm_nominal), "warm_radius": wire(warm_radius),
            "warm_interval": [wire(warm_lower), wire(warm_upper)], "cold_interval": ["60", "60"],
            "stop_interval": ["0", "0"], "competitor_dominance": True,
            "scope": "Exact arithmetic reproduction of the published one-continuation-step fixture; no fresh Lean selector call"},
        "completion_order": {"four_cases": four_cases, "first_report_success": wire(first_mass),
            "twenty_count_classes": twenty, "represented_vectors": 2 ** 20,
            "lower_bound_event_mass": wire(lower_bound), "exact_interval_miss_mass": wire(exact_miss)},
        "completion_conditioning": {"deadline_cases": deadline, "completion_mass": wire(completion_mass),
            "conditional_first_success": wire(conditional_first), "unconditional_first_success": "1/2",
            "outcome_censoring_retained_success": wire(conditional_retained)},
        "replay_prefixes": replay_prefixes,
        "non_claims": ["No new Lean compilation was run", "No universal Python/Lean refinement",
            "No verification of physical source-law assumptions, authentic reports, durable storage, or measured hardware costs",
            "The exact completion-order counterexample refutes an external applicability shortcut, not the formal source-generative theorem",
            "Binary count-class reduction is valid for this specified success-before-rejection ordering only"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed", "count_mass_checks": mathematical["count_mass_checks"],
        "independent_sequence_checks": mathematical["independent_sequence_checks"], "interface_checks": len(interface),
        "release_files_unchanged": len(before), "completion_order_lower_bound": wire(lower_bound),
        "n500_band": fixture["probability_band"], "runtime_seconds": result["runtime_seconds"]}))


if __name__ == "__main__":
    main()
