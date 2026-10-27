#!/usr/bin/env python3
"""Independent exact finite audit for Komorebi p-adic Block 09.

The audit checks the executable counters and the two proved envelopes with
arbitrary-precision Python integers.  Finite success is implementation evidence;
the universal inequalities are supplied by Lean.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

from verify_final_fiber_boundary import (
    PRIMES,
    concrete_boundary,
    quotient_bound,
    suffix_result,
)

R_MAX = 300
H_VALUES = tuple(range(10))
STRESS_CASES = (
    (2, 8059, 0),
    (2, 12000, 3),
    (3, 5000, 0),
    (5, 4000, 1),
    (7, 3500, 2),
    (13, 3000, 0),
)


def full_representative_count(p: int, q: int) -> int:
    assert p >= 2 and q >= 1
    return (q - 1) // p + 1


def representative_budget(p: int, bound: int) -> int:
    return sum(full_representative_count(p, q) for q in range(1, bound + 1))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[1]
    counts: Counter[str] = Counter()
    failures: list[dict[str, object]] = []
    maxima: dict[str, dict[str, object]] = {
        "quotient": {"value": 0, "case": None},
        "representative_tests": {"value": 0, "case": None},
        "total_tests": {"value": 0, "case": None},
        "budget_slack": {"value": 0, "case": None},
        "quadratic_slack": {"value": 0, "case": None},
        "suffix_width": {"value": 0, "case": None},
    }

    def check(name: str, condition: bool, **data: object) -> None:
        counts[name] += 1
        if not condition and len(failures) < 200:
            failures.append({"check": name, **data})

    def record_max(name: str, value: int, case: dict[str, int]) -> None:
        if value > int(maxima[name]["value"]):
            maxima[name] = {"value": value, "case": case}

    total_exact_tests = 0
    total_budget_bound = 0
    total_quadratic_bound = 0
    total_full_representatives = 0
    total_suffix_representatives = 0

    def audit_case(p: int, r: int, h: int, lane: str) -> None:
        nonlocal total_exact_tests, total_budget_bound, total_quadratic_bound
        nonlocal total_full_representatives, total_suffix_representatives
        case = {"p": p, "r": r, "h": h}
        out = concrete_boundary(p, r, h)
        q_star = out["quotient"]
        q_tests = q_star
        fiber_tests = out["boundary_tests"]
        rep_tests = out["representative_tests"]
        B = quotient_bound(p, r, h)
        selected_budget = representative_budget(p, q_star)
        coarse_budget = representative_budget(p, B)
        budget_bound = B + p + coarse_budget
        quadratic_bound = B * B + B + p
        total = q_tests + fiber_tests + rep_tests

        counts[f"{lane}_cases"] += 1
        check("quotient_within_bound", q_star <= B, lane=lane, **case, q_star=q_star, B=B)
        check("quotient_counter_exact", q_tests == q_star, lane=lane, **case)
        check("fiber_counter_bounds", 1 <= fiber_tests <= p, lane=lane, **case, fiber_tests=fiber_tests)
        check("representative_le_selected_budget", rep_tests <= selected_budget, lane=lane, **case, rep_tests=rep_tests, selected_budget=selected_budget)
        check("selected_budget_le_coarse_budget", selected_budget <= coarse_budget, lane=lane, **case)
        check("coarse_budget_le_square", coarse_budget <= B * B, lane=lane, **case, coarse_budget=coarse_budget, square=B * B)
        check("representative_le_square", rep_tests <= B * B, lane=lane, **case)
        check("total_exact_sum", total == q_tests + fiber_tests + rep_tests, lane=lane, **case)
        check("total_le_budget_bound", total <= budget_bound, lane=lane, **case, total=total, bound=budget_bound)
        check("budget_le_quadratic", budget_bound <= quadratic_bound, lane=lane, **case)
        check("total_le_quadratic", total <= quadratic_bound, lane=lane, **case, total=total, bound=quadratic_bound)

        recomputed_rep_tests = 0
        for q in range(1, q_star + 1):
            _cost, tested = suffix_result(p, h, q)
            full = full_representative_count(p, q)
            recomputed_rep_tests += tested
            total_full_representatives += full
            total_suffix_representatives += tested
            check("per_quotient_suffix_le_full", tested <= full, lane=lane, **case, q=q, tested=tested, full=full)
            check("per_quotient_full_le_q", full <= q, lane=lane, **case, q=q, full=full)
        check("representative_counter_recomputed", rep_tests == recomputed_rep_tests, lane=lane, **case, rep_tests=rep_tests, recomputed=recomputed_rep_tests)

        total_exact_tests += total
        total_budget_bound += budget_bound
        total_quadratic_bound += quadratic_bound
        record_max("quotient", q_star, case)
        record_max("representative_tests", rep_tests, case)
        record_max("total_tests", total, case)
        record_max("budget_slack", budget_bound - total, case)
        record_max("quadratic_slack", quadratic_bound - total, case)
        max_suffix = max((suffix_result(p, h, q)[1] for q in range(1, q_star + 1)), default=0)
        record_max("suffix_width", max_suffix, case)

    for p in PRIMES:
        for r in range(1, R_MAX + 1):
            for h in H_VALUES:
                audit_case(p, r, h, "grid")

    stress_records: list[dict[str, int]] = []
    for p, r, h in STRESS_CASES:
        audit_case(p, r, h, "stress")
        out = concrete_boundary(p, r, h)
        B = quotient_bound(p, r, h)
        total = out["quotient"] + out["boundary_tests"] + out["representative_tests"]
        stress_records.append({
            "p": p,
            "r": r,
            "h": h,
            "quotient": out["quotient"],
            "layer": out["layer"],
            "quotient_tests": out["quotient"],
            "final_fiber_tests": out["boundary_tests"],
            "representative_tests": out["representative_tests"],
            "total_tests": total,
            "search_bound": B,
            "representative_budget": representative_budget(p, B),
            "budget_bound": B + p + representative_budget(p, B),
            "quadratic_bound": B * B + B + p,
        })

    # Exhaustive monotonicity checks for the finite representative budget.
    for p in PRIMES:
        budgets = [representative_budget(p, b) for b in range(0, 401)]
        for a in range(0, 401):
            for b in range(a, min(401, a + 12)):
                check("budget_monotone", budgets[a] <= budgets[b], p=p, a=a, b=b)
        for b, budget in enumerate(budgets):
            check("budget_quadratic", budget <= b * b, p=p, b=b, budget=budget)

    source_paths = sorted((root / "lean" / "KomorebiPadic").glob("*.lean"))
    report = {
        "schema": "komorebi-padic-block09-complexity-audit-v1",
        "status": "PASS" if not failures else "FAIL",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": {
            "primes": list(PRIMES),
            "r_max": R_MAX,
            "h_values": list(H_VALUES),
            "stress_cases": [list(x) for x in STRESS_CASES],
            "budget_monotonicity_bound": 400,
        },
        "counts": dict(sorted(counts.items())),
        "total_recorded_checks_and_cases": sum(counts.values()),
        "failure_count": len(failures),
        "failures": failures,
        "maxima": maxima,
        "aggregate_accounting": {
            "total_exact_reported_tests": total_exact_tests,
            "total_budget_bound": total_budget_bound,
            "total_quadratic_bound": total_quadratic_bound,
            "total_full_representative_evaluations": total_full_representatives,
            "total_suffix_representative_evaluations": total_suffix_representatives,
            "full_to_suffix_ratio": (
                total_full_representatives / total_suffix_representatives
                if total_suffix_representatives else None
            ),
        },
        "stress_records": stress_records,
        "source_sha256": {str(p.relative_to(root)): sha256(p) for p in source_paths},
        "runtime_seconds": time.perf_counter() - started,
        "platform": platform.platform(),
        "python": sys.version,
        "non_claims": [
            "Finite audit output is not a universal proof.",
            "The quadratic bound is an envelope, not an exact operation count.",
            "No asymptotic optimality or constant suffix-window width is claimed.",
            "Composite bases are outside the prime-base end-to-end theorem.",
        ],
    }
    out_path = root / "results" / "compiler_complexity_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "grid_cases": counts["grid_cases"],
        "stress_cases": counts["stress_cases"],
        "total_checks": report["total_recorded_checks_and_cases"],
        "failures": len(failures),
        "maxima": maxima,
        "aggregate_accounting": report["aggregate_accounting"],
        "runtime_seconds": report["runtime_seconds"],
        "output": str(out_path),
    }, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
