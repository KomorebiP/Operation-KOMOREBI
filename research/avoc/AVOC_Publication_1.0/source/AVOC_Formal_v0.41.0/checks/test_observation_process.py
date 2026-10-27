#!/usr/bin/env python3
"""Exact bounded observation-process oracle; no stochastic simulation.

Two constructions independently enumerate the same finite experiment.  The
latent construction preloads every identity's complete binary stream, then
enumerates auxiliary fault tapes.  The tree construction generates a Bernoulli
report only after the predictable fault decision admits the current attempt.
Neither construction calls the production interval evaluator to compute mass.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import calibrate_quote as production

POLICIES = ("alternate_no_fault", "success_switch_history_fault",
            "fault_aware_history", "stop_on_first_rejection")
PARAMETERS = ((Q(0), Q(1)), (Q(1, 2), Q(1, 2)), (Q(1, 10), Q(9, 10)),
              (Q(1, 3), Q(2, 3)), (Q(1), Q(0)))
ALPHA = Q(1, 20)
GRID_CELLS = 100
SCHEDULE = ((0, 1), (0, 2), (1, 1), (1, 2))
BASELINE_SHA256 = "298b6daed3875697a59c15caa6d8546c9cfe2d30aa8cfbc4aab0275ad63be44c"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def equal(left, right, message):
    if left != right:
        raise AssertionError(f"{message}: {left!r} != {right!r}")


def wire(value):
    value = Q(value)
    return value.numerator if value.denominator == 1 else str(value)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decision(policy, trace):
    """Predictable choice and fault probability: reads public trace only.

    An event is (identity index, outcome), with -1 denoting a fault and 0/1
    denoting an admitted checked rejection/success. Faults never advance the
    report cursor. None means stop without an additional attempt.
    """
    t = len(trace)
    successes = sum(outcome == 1 for _, outcome in trace)
    faults = sum(outcome == -1 for _, outcome in trace)
    if policy == "alternate_no_fault":
        return t % 2, Q(0)
    if policy == "success_switch_history_fault":
        identity = 0 if not trace else (1 - trace[-1][0] if trace[-1][1] == 1 else trace[-1][0])
        return identity, Q((t + 2 * identity + successes) % 3, 3)
    if policy == "fault_aware_history":
        identity = (successes + faults) % 2
        return identity, Q(1, 2) if trace and trace[-1][1] == -1 else Q(1, 3)
    if policy == "stop_on_first_rejection":
        if any(outcome == 0 for _, outcome in trace):
            return None
        return 0, Q(1, 2) if t % 2 else Q(0)
    raise ValueError(policy)


def reports(trace, identity):
    return tuple(outcome for j, outcome in trace if j == identity and outcome != -1)


def convolution(n, p):
    answer = [Q(1)]
    for _ in range(n):
        following = [Q(0)] * (len(answer) + 1)
        for k, mass in enumerate(answer):
            following[k] += mass * (1 - p)
            following[k + 1] += mass * p
        answer = following
    return answer


def unfold_tree(horizon, probabilities, policy):
    """Generative tree, without preload, binomial formula, or fault tape."""
    terminal = defaultdict(Q)
    def visit(trace, mass):
        if not mass:
            return
        choice = decision(policy, trace) if len(trace) < horizon else None
        if choice is None:
            terminal[trace] += mass
            return
        identity, fault = choice
        check(0 <= fault <= 1, "fault probability outside [0,1]")
        visit(trace + ((identity, -1),), mass * fault)
        visit(trace + ((identity, 0),), mass * (1 - fault) * (1 - probabilities[identity]))
        visit(trace + ((identity, 1),), mass * (1 - fault) * probabilities[identity])
    visit((), Q(1))
    return dict(terminal)


def enumerate_latent(horizon, probabilities, policy):
    """Full latent prefixes + binary auxiliary tape; unused tape bits integrate out.

    The auxiliary tape is weighted by history-dependent transition kernels, not
    claimed to have independent identically distributed fault bits.  Once the
    process stops, remaining tape bits use fair independent padding, making each
    complete latent prefix's summed auxiliary weight exactly one.
    """
    terminal = defaultdict(Q)
    prefix_laws = {(j, n): [Q(0)] * (n + 1)
                   for j in range(2) for n in range(horizon + 1)}
    tables = 0
    path_checks = 0
    for flat in product((0, 1), repeat=2 * horizon):
        streams = (flat[:horizon], flat[horizon:])
        latent_mass = Q(1)
        for j, stream in enumerate(streams):
            for bit in stream:
                latent_mass *= probabilities[j] if bit else 1 - probabilities[j]
        fault_weight_sum = Q(0)
        for tape in product((0, 1), repeat=horizon):
            tables += 1
            trace = ()
            cursors = [0, 0]
            fault_weight = Q(1)
            stopped = False
            for fault_bit in tape:
                choice = None if stopped else decision(policy, trace)
                if choice is None:
                    stopped = True
                    fault_weight *= Q(1, 2)
                    continue
                identity, fault_probability = choice
                fault_weight *= fault_probability if fault_bit else 1 - fault_probability
                if fault_bit:
                    outcome = -1
                else:
                    outcome = streams[identity][cursors[identity]]
                    cursors[identity] += 1
                trace += ((identity, outcome),)
            fault_weight_sum += fault_weight
            if latent_mass * fault_weight:
                terminal[trace] += latent_mass * fault_weight
            # Check even zero-weight rows: prefix preservation is pathwise.
            for j in range(2):
                equal(reports(trace, j), streams[j][:cursors[j]], "pathwise stream-prefix preservation")
                path_checks += 1
        equal(fault_weight_sum, Q(1), "auxiliary kernel normalizes for each fixed latent stream")
        for (j, n), law in prefix_laws.items():
            law[sum(streams[j][:n])] += latent_mass * fault_weight_sum
    for (j, n), law in prefix_laws.items():
        equal(law, convolution(n, probabilities[j]), "latent prefix count law versus independent convolution")
    return dict(terminal), tables, path_checks, len(prefix_laws)


@lru_cache(maxsize=None)
def independent_interval(n, k, alpha=ALPHA, cells=GRID_CELLS):
    """Enumerate report strings, not choose(n,k), to construct the cell envelope."""
    retained = []
    threshold = alpha / (n + 1)
    for cell in range(cells):
        lower, upper = Q(cell, cells), Q(cell + 1, cells)
        envelope = Q(0)
        for bits in product((0, 1), repeat=n):
            if sum(bits) == k:
                factor = Q(1)
                for bit in bits:
                    factor *= upper if bit else 1 - lower
                envelope += factor
        if envelope > threshold:
            retained.append(cell)
    return (Q(retained[0], cells), Q(retained[-1] + 1, cells)) if retained else (Q(0), Q(1))


def identities():
    base = json.loads((ROOT / "examples/robust_quote/uncertain_plan.json").read_text())
    return (base[3][0], base[4][0])


def request_for(trace, selected, checkpoint, duplicate=True):
    ids = identities()
    events = [{"operation_id": f"attempt-{i}", "identity": ids[j],
               "status": {-1: "infrastructure_fault", 0: "checked_rejection", 1: "checked_success"}[outcome],
               "evidence_id": f"protected-report-{i}"} for i, (j, outcome) in enumerate(trace)]
    if duplicate and events:
        events.append(deepcopy(events[0]))
    return {
        "schema": "avoc-calibration-v1",
        "authority": {"authority_id": "prospective-observation-oracle-v040", "total_alpha": "1/5",
                      "grid": [wire(Q(i, GRID_CELLS)) for i in range(GRID_CELLS + 1)],
                      "strata": [{"identity": ids[j], "checkpoints": [{"n": n, "alpha": wire(ALPHA)}
                                                                          for identity, n in SCHEDULE if identity == j]}
                                 for j in range(2)]},
        "selected_identity": ids[selected], "checkpoint": checkpoint, "events": events,
    }


def expect_rejection(request, text):
    try:
        production.calibrate(request)
    except production.CalibrationError as error:
        check(text in str(error), f"unexpected rejection: {error}")
        return
    raise AssertionError("request was accepted: " + text)


@lru_cache(maxsize=None)
def parser_check(trace, j, n):
    observed = reports(trace, j)
    request = request_for(trace, j, n)
    if len(observed) < n:
        expect_rejection(request, "not enough checked binary outcomes")
        return "incomplete-rejected"
    actual = production.calibrate(request)
    count = sum(observed[:n])
    equal(actual["successes"], count, "actual parser preserves first n checked reports")
    equal(tuple(Q(x) for x in actual["probability_band"]), independent_interval(n, count),
          "actual parser versus independent cell-envelope interval")
    equal(actual["duplicate_reports_ignored"], int(bool(trace)), "actual parser ignores exact replay")
    equal(actual["checked_reports_beyond_checkpoint"], len(observed) - n, "post-checkpoint report accounting")
    equal(actual["selected_stratum_status_counts"]["infrastructure_fault"],
          sum(identity == j and bit == -1 for identity, bit in trace), "actual parser fault accounting")
    return "complete-calibrated"


def coverage(terminal, probabilities):
    equal(sum(terminal.values()), Q(1), "trace law normalization")
    completed = {pair: Q(0) for pair in SCHEDULE}
    bad_issued = {pair: Q(0) for pair in SCHEDULE}
    any_bad = Q(0)
    selected_bad = Q(0)
    selected_any = Q(0)
    for trace, mass in terminal.items():
        available = []
        bad = set()
        for j, n in SCHEDULE:
            parser_check(trace, j, n)
            observed = reports(trace, j)
            if len(observed) >= n:
                completed[(j, n)] += mass
                count = sum(observed[:n])
                available.append((j, n, count))
                lower, upper = independent_interval(n, count)
                if not lower <= probabilities[j] <= upper:
                    bad_issued[(j, n)] += mass
                    bad.add((j, n))
        if bad:
            any_bad += mass
        if available:
            selected_any += mass
            # Entirely data-dependent identity and checkpoint selection.
            j, n, _ = max(available, key=lambda x: (Q(abs(2 * x[2] - x[1]), x[1]), x[1], x[0]))
            if (j, n) in bad:
                selected_bad += mass
    for pair, value in bad_issued.items():
        j, n = pair
        latent_bad = sum(mass for k, mass in enumerate(convolution(n, probabilities[j]))
                         if not independent_interval(n, k)[0] <= probabilities[j] <= independent_interval(n, k)[1])
        check(value <= latent_bad <= ALPHA, "unconditional issued-bad mass exceeds latent-prefix bound")
    check(selected_bad <= any_bad <= sum(bad_issued.values()) <= len(SCHEDULE) * ALPHA,
          "finite schedule or selected output exceeds total allocation")
    return {"completion_masses": {f"identity{j}_n{n}": wire(value) for (j, n), value in completed.items()},
            "bad_issued_masses": {f"identity{j}_n{n}": wire(value) for (j, n), value in bad_issued.items()},
            "any_bad_issued_mass": wire(any_bad), "selected_bad_issued_mass": wire(selected_bad),
            "any_selected_mass": wire(selected_any)}


def counterexamples():
    # A report is produced only on a successful attempt; failed attempts consume
    # a hidden bit and are mislabeled/excluded as infrastructure faults.
    p = Q(1, 10)
    attempts = 20
    distribution = convolution(attempts, p)
    issued_mass = sum(distribution[2:])
    interval = independent_interval(2, 2)
    check(not interval[0] <= p <= interval[1], "counterexample interval unexpectedly contains target p")
    check(issued_mass > ALPHA, "outcome-dependent thinning did not violate allocated alpha")
    selected_success_mass = Q(1, 2)
    selected_total_mass = Q(1, 2)
    equal(selected_success_mass / selected_total_mass, Q(1), "fair attempted outcome censored to certain success")
    # Stop immediately after a first rejection; otherwise obtain exactly n=2.
    complete = Q(0)
    bad = Q(0)
    first_success_given_complete = Q(0)
    for bits in product((0, 1), repeat=2):
        mass = (p if bits[0] else 1 - p) * (p if bits[1] else 1 - p)
        if bits[0] == 1:
            complete += mass
            first_success_given_complete += mass
            lower, upper = independent_interval(2, sum(bits))
            if not lower <= p <= upper:
                bad += mass
    equal((complete, bad, bad / complete), (Q(1, 10), Q(1, 100), Q(1, 10)),
          "completion conditioning counterexample")
    check(bad <= ALPHA < bad / complete, "conditional and unconditional guarantees conflated")
    equal(first_success_given_complete / complete, Q(1), "completion reveals first success")
    # With no consumption, even outcome-dependent blocking preserves prefixes.
    # Use the first latent bit only when it is success; failure blocks forever.
    blocked_issue_bad = p * p  # Both first two bits success is the sole n=2 completion.
    check(blocked_issue_bad <= ALPHA, "no-consumption blocking violated pathwise subset bound")
    return {
        "outcome_dependent_consuming_faults": {
            "attempt_probability": "1/10", "attempts": attempts, "required_checked_reports": 2,
            "rule": "consume each attempted bit; report success, label rejection a fault and exclude it",
            "issued_interval": [wire(x) for x in interval], "bad_issued_mass": wire(issued_mass),
            "allocated_alpha": wire(ALPHA), "violates_unconditional_budget": True,
            "one_fair_attempt_retained_success_probability": 1},
        "conditioning_on_completion": {
            "probability": "1/10", "checkpoint": 2, "rule": "stop after first rejection",
            "completion_mass": wire(complete), "unconditional_bad_issued_mass": wire(bad),
            "bad_given_completion": wire(bad / complete), "allocated_alpha": wire(ALPHA),
            "first_success_given_completion": 1, "violates_conditional_budget_only": True},
        "outcome_dependent_nonconsuming_block": {
            "rule": "block on a rejection forever without advancing the latent report cursor",
            "bad_issued_mass": wire(blocked_issue_bad), "preserves_unconditional_prefix_bound": True},
    }


def interface_boundaries():
    checks = []
    trace = ((0, 1), (1, 0), (0, -1), (0, 0), (0, 1))
    base = request_for(trace, 0, 2)
    equal(json.loads((ROOT / "examples/observation_process/complete_prefix.json").read_text()),
          base, "complete-prefix fixture matches tested request")
    result = production.calibrate(base)
    equal(result["successes"], 1, "success and rejection both retained in first prefix")
    checks.append("retain both outcomes; exclude faults; exact replay idempotent; later report ignored")
    changed = deepcopy(base)
    changed["events"][-1]["status"] = "checked_rejection"
    expect_rejection(changed, "conflicting replay")
    checks.append("changed operation replay rejected")
    insufficient = request_for(((0, 1), (0, -1), (1, 1)), 0, 2)
    equal(json.loads((ROOT / "examples/observation_process/insufficient_prefix.json").read_text()),
          insufficient, "insufficient-prefix fixture matches tested request")
    expect_rejection(insufficient, "not enough checked binary outcomes")
    checks.append("fault and other identity cannot complete selected checkpoint")
    undeclared = deepcopy(base)
    undeclared["checkpoint"] = 3
    expect_rejection(undeclared, "not predeclared")
    checks.append("unregistered checkpoint rejected")
    # The parser cannot detect maliciously missing records. Exhibit the boundary
    # openly: deleting a rejection makes a different accepted input, not evidence
    # that retention or completeness has been authenticated.
    thinned = request_for(((0, 1), (0, 1)), 0, 2)
    equal(json.loads((ROOT / "examples/observation_process/thinned_log_trust_boundary.json").read_text()),
          thinned, "thinned-log fixture matches tested request")
    equal(production.calibrate(thinned)["successes"], 2, "parser complete-log trust boundary")
    checks.append("parser accepts a thinned supplied log; completeness remains a trusted premise")
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results/v0.40.0/oracle_results.json")
    args = parser.parse_args()
    started = time.perf_counter()
    sources = ["checks/test_observation_process.py", "tools/calibrate_quote.py",
               "examples/robust_quote/uncertain_plan.json", "examples/observation_process/contract.json",
               "examples/observation_process/complete_prefix.json",
               "examples/observation_process/insufficient_prefix.json",
               "examples/observation_process/thinned_log_trust_boundary.json"]
    before = {path: sha256(ROOT / path) for path in sources}
    rows = []
    tables = path_checks = prefix_checks = trace_comparisons = 0
    for horizon in range(5):
        for probabilities in PARAMETERS:
            for policy in POLICIES:
                latent, count, prefix_paths, prefix_laws = enumerate_latent(horizon, probabilities, policy)
                tree = unfold_tree(horizon, probabilities, policy)
                equal(latent, tree, "independent latent enumeration versus generative attempt tree")
                row = {"horizon": horizon, "probabilities": [wire(x) for x in probabilities],
                       "policy": policy, "positive_terminal_traces": len(tree)}
                row.update(coverage(tree, probabilities))
                rows.append(row)
                tables += count
                path_checks += prefix_paths
                prefix_checks += prefix_laws
                trace_comparisons += len(tree)
    failures = counterexamples()
    boundaries = interface_boundaries()
    after = {path: sha256(ROOT / path) for path in sources}
    equal(before, after, "scientific inputs changed during execution")
    result = {
        "status": "passed", "kind": "exact finite evidence, not a universal theorem",
        "coefficient_domain": "Python arbitrary-precision int and fractions.Fraction; no floating probability arithmetic",
        "source_sha256": after, "baseline_zip_sha256": BASELINE_SHA256,
        "python_version": platform.python_version(), "command": ["python3", "checks/test_observation_process.py", *sys.argv[1:]],
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "ranges": {"attempt_horizons": [0, 4], "identity_count": 2,
                   "probability_pairs": [[wire(x) for x in ps] for ps in PARAMETERS], "policies": list(POLICIES),
                   "schedule": [[j, n, wire(ALPHA)] for j, n in SCHEDULE], "grid_cells": GRID_CELLS,
                   "consuming_censor_counterexample_attempts": 20},
        "counts": {"experiment_cases": len(rows), "full_latent_auxiliary_table_rows": tables,
                   "pathwise_prefix_checks_including_zero_weight_rows": path_checks,
                   "latent_prefix_count_law_checks": prefix_checks,
                   "positive_trace_mass_comparisons": trace_comparisons,
                   "actual_parser_unique_trace_checkpoint_checks": parser_check.cache_info().misses,
                   "coverage_schedule_cases": len(rows), "extra_interface_boundary_checks": len(boundaries)},
        "counterexamples": failures, "interface_boundaries": boundaries, "case_results": rows,
        "non_claims": ["Bounded enumeration does not prove all horizons or all policies.",
                       "No empirical operation measurements or authentication of logged reports.",
                       "No proof that real failures are noninformative or leave the next latent checked report unchanged.",
                       "No guarantee conditional on successful checkpoint completion.",
                       "No retroactive authority registration, unlimited optional stopping, or probability drift.",
                       "The actual existing Python parser is exercised; no universal Python-to-Lean refinement is claimed.",
                       "No operation, retry, deployment, or plan acknowledgement is performed."],
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "output": str(output.relative_to(ROOT)),
                      "counts": result["counts"], "runtime_seconds": result["runtime_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
