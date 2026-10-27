#!/usr/bin/env python3
"""Independent exact audit for Komorebi p-adic Block 08.

This script tests the generic descending first-true algorithm and the concrete
final-fiber boundary compiler with arbitrary-precision integer arithmetic.
Finite success is implementation evidence only; universal correctness is
supplied by the compiled Lean theorems.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import sys
import time
from collections import Counter
from pathlib import Path

PRIMES = (2, 3, 5, 7, 11, 13)
R_MAX = 240
H_VALUES = tuple(range(10))
DIRECT_PRIMES = (2, 3, 5, 7)
DIRECT_R_MAX = 80
DIRECT_H_VALUES = tuple(range(6))
STRESS_CASES = (
    (2, 8059, 0),
    (2, 12000, 3),
    (3, 5000, 0),
    (5, 4000, 1),
    (7, 3500, 2),
    (13, 3000, 0),
)


def vp_factorial(n: int, p: int) -> int:
    assert n >= 0 and p >= 2
    out = 0
    while n:
        n //= p
        out += n
    return out


def vp_binom(n: int, k: int, p: int) -> int:
    assert 0 <= k <= n
    return vp_factorial(n, p) - vp_factorial(k, p) - vp_factorial(n - k, p)


def vp_integer(n: int, p: int) -> int:
    assert n > 0
    out = 0
    while n % p == 0:
        n //= p
        out += 1
    return out


def branch_cost(h: int, k: int, carry: int) -> int:
    return k * (h + 1) + carry


def coarse_k(r: int, h: int) -> int:
    return max(r - 1, 0) // (h + 1)


def quotient_bound(p: int, r: int, h: int) -> int:
    return coarse_k(r, h) // (p - 1) + 1


def representative(p: int, q_bound: int, a: int) -> int:
    return min(q_bound, p * (a + 1))


def suffix_result(p: int, h: int, q_bound: int) -> tuple[int, int]:
    assert q_bound >= 1
    a_max = (q_bound - 1) // p

    def visible(a: int) -> int:
        return (p * q_bound - representative(p, q_bound, a)) * (h + 1)

    def cost(a: int) -> int:
        return visible(a) + vp_binom(q_bound - 1, a, p)

    best = cost(a_max)
    tested = 1
    for a in range(a_max - 1, -1, -1):
        if best <= visible(a):
            break
        best = min(best, cost(a))
        tested += 1
    return best, tested


def first_noncrossing(p: int, r: int, h: int) -> tuple[int, int]:
    bound = quotient_bound(p, r, h)
    rep_tests = 0
    for q in range(1, bound + 1):
        cost, tested = suffix_result(p, h, q)
        rep_tests += tested
        if cost >= r:
            return q, rep_tests
    raise AssertionError("terminal quotient unexpectedly crosses")


def target_compiler(p: int, r: int, h: int, q_bound: int, t: int) -> bool:
    if t <= 0:
        return False
    for q in range(1, min(q_bound, t) + 1):
        k = t - q
        if branch_cost(h, k, vp_binom(t - 1, k, p)) < r:
            return True
    return False


def direct_target_set(p: int, r: int, h: int, q_bound: int) -> set[int]:
    K = coarse_k(r, h)
    out: set[int] = set()
    for q in range(1, q_bound + 1):
        for k in range(K + 1):
            if branch_cost(h, k, vp_binom(q + k - 1, k, p)) < r:
                out.add(q + k)
    return out


def descending_first_true(pred, lower: int, upper: int) -> tuple[int, int]:
    assert lower <= upper
    tested = 0
    for t in range(upper, lower - 1, -1):
        tested += 1
        if pred(t):
            return t, tested
    # This branch is excluded in the proved use by the certified true lower endpoint.
    return max(lower - 1, 0), tested


def concrete_boundary(p: int, r: int, h: int) -> dict[str, int]:
    q_star, rep_tests = first_noncrossing(p, r, h)
    lower = max(1, p * (q_star - 1))
    upper = p * q_star - 1
    pred = lambda t: target_compiler(p, r, h, q_star, t)
    layer, boundary_tests = descending_first_true(pred, lower, upper)
    reference = max(t for t in range(lower, upper + 1) if pred(t))
    return {
        "quotient": q_star,
        "lower": lower,
        "upper": upper,
        "layer": layer,
        "reference": reference,
        "boundary_tests": boundary_tests,
        "full_tests": upper + 1 - lower,
        "representative_tests": rep_tests,
    }


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
        "boundary_tests": {"value": 0, "case": None},
        "full_tests": {"value": 0, "case": None},
        "tests_saved": {"value": 0, "case": None},
        "quotient": {"value": 0, "case": None},
        "layer": {"value": 0, "case": None},
    }
    total_full_tests = 0
    total_boundary_tests = 0

    def check(name: str, condition: bool, **data: object) -> None:
        counts[name] += 1
        if not condition and len(failures) < 200:
            failures.append({"check": name, **data})

    def record_max(name: str, value: int, case: dict[str, int]) -> None:
        if value > int(maxima[name]["value"]):
            maxima[name] = {"value": value, "case": case}

    # Exhaust all Boolean patterns up to length 14 whose lowest point is true.
    generic_patterns = 0
    for length in range(1, 15):
        lower = 3
        upper = lower + length - 1
        for tail in itertools.product((False, True), repeat=length - 1):
            values = (True, *tail)  # little-endian: lower first
            pred = lambda i, values=values: values[i - lower]
            value, tested = descending_first_true(pred, lower, upper)
            true_indices = [lower + i for i, b in enumerate(values) if b]
            expected = max(true_indices)
            generic_patterns += 1
            check("generic_value", value == expected, length=length, values=values, value=value, expected=expected)
            check("generic_tested", tested == upper - expected + 1, length=length, values=values, tested=tested)
            check("generic_bounds", lower <= value <= upper, length=length, value=value)
            check("generic_result_true", pred(value), length=length, value=value)
            check("generic_all_above_false", all(not pred(i) for i in range(value + 1, upper + 1)), length=length, value=value)

    # Main concrete grid.
    for p in PRIMES:
        for r in range(1, R_MAX + 1):
            for h in H_VALUES:
                case = {"p": p, "r": r, "h": h}
                out = concrete_boundary(p, r, h)
                q = out["quotient"]
                M = out["layer"]
                lo = out["lower"]
                hi = out["upper"]
                bt = out["boundary_tests"]
                ft = out["full_tests"]
                total_full_tests += ft
                total_boundary_tests += bt
                counts["concrete_cases"] += 1

                check("boundary_equals_reference", M == out["reference"], **case, out=out)
                check("lower_is_target", target_compiler(p, r, h, q, lo), **case, out=out)
                check("boundary_is_target", target_compiler(p, r, h, q, M), **case, out=out)
                check("all_above_boundary_false", all(not target_compiler(p, r, h, q, t) for t in range(M + 1, hi + 1)), **case, out=out)
                check("test_distance", bt == hi - M + 1, **case, out=out)
                check("test_positive", 1 <= bt, **case, out=out)
                check("test_le_base", bt <= p, **case, out=out)
                check("test_le_full_width", bt <= ft, **case, out=out)
                check("full_width_le_base", ft <= p, **case, out=out)
                check("fixed_point", M // p + 1 == q, **case, out=out)
                check("terminal_quotient_noncrossing", suffix_result(p, h, q)[0] >= r, **case, out=out)
                check("earlier_quotients_cross", all(suffix_result(p, h, j)[0] < r for j in range(1, q)), **case, out=out)

                record_max("boundary_tests", bt, case)
                record_max("full_tests", ft, case)
                record_max("tests_saved", ft - bt, case)
                record_max("quotient", q, case)
                record_max("layer", M, case)

    # Independent edge-image lane.
    direct_cases = 0
    for p in DIRECT_PRIMES:
        for r in range(1, DIRECT_R_MAX + 1):
            for h in DIRECT_H_VALUES:
                case = {"p": p, "r": r, "h": h}
                out = concrete_boundary(p, r, h)
                targets = direct_target_set(p, r, h, out["quotient"])
                direct_cases += 1
                check("direct_nonempty", bool(targets), **case)
                check("direct_initial_interval", targets == set(range(1, max(targets) + 1)), **case)
                check("direct_maximum", out["layer"] == max(targets), **case, out=out, direct=max(targets))
                for t in range(out["lower"], out["upper"] + 1):
                    check("direct_target_compiler", target_compiler(p, r, h, out["quotient"], t) == (t in targets), **case, t=t)

    # Direct integer-binomial valuation checks on an independent small lane.
    integer_binom_checks = 0
    for p in PRIMES:
        for n in range(0, 45):
            for k in range(0, n + 1):
                integer_binom_checks += 1
                b = math.comb(n, k)
                check("integer_binomial_valuation", vp_binom(n, k, p) == vp_integer(b, p), p=p, n=n, k=k)

    stress_records: list[dict[str, int]] = []
    for p, r, h in STRESS_CASES:
        out = concrete_boundary(p, r, h)
        record = {"p": p, "r": r, "h": h, **out}
        stress_records.append(record)
        check("stress_boundary_equals_reference", out["layer"] == out["reference"], **record)
        check("stress_test_bounds", 1 <= out["boundary_tests"] <= p, **record)
        check("stress_distance", out["boundary_tests"] == out["upper"] - out["layer"] + 1, **record)

    source_paths = sorted((root / "lean" / "KomorebiPadic").glob("*.lean"))
    source_hashes = {str(p.relative_to(root)): sha256(p) for p in source_paths}
    total_checks = sum(counts.values())
    elapsed = time.perf_counter() - started
    report = {
        "schema": "komorebi-padic-block08-boundary-audit-v1",
        "status": "PASS" if not failures else "FAIL",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": {
            "primes": list(PRIMES),
            "r_max": R_MAX,
            "h_values": list(H_VALUES),
            "direct_primes": list(DIRECT_PRIMES),
            "direct_r_max": DIRECT_R_MAX,
            "direct_h_values": list(DIRECT_H_VALUES),
            "generic_max_length": 14,
            "stress_cases": [list(x) for x in STRESS_CASES],
        },
        "generic_patterns": generic_patterns,
        "concrete_cases": counts["concrete_cases"],
        "direct_cases": direct_cases,
        "integer_binomial_checks": integer_binom_checks,
        "counts": dict(sorted(counts.items())),
        "total_recorded_checks_and_cases": total_checks,
        "failure_count": len(failures),
        "failures": failures,
        "maxima": maxima,
        "accounting": {
            "total_full_final_fiber_tests": total_full_tests,
            "total_boundary_tests": total_boundary_tests,
            "tests_saved": total_full_tests - total_boundary_tests,
            "full_to_boundary_ratio": total_full_tests / total_boundary_tests if total_boundary_tests else None,
        },
        "stress_records": stress_records,
        "source_sha256": source_hashes,
        "runtime_seconds": elapsed,
        "platform": platform.platform(),
        "python": sys.version,
        "non_claims": [
            "Finite audit output is not a universal proof.",
            "No constant boundary-test count smaller than p is inferred.",
            "Composite bases are outside the checked prime-base theorem.",
        ],
    }
    out_path = root / "results" / "final_fiber_boundary_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "generic_patterns": generic_patterns,
        "concrete_cases": report["concrete_cases"],
        "direct_cases": direct_cases,
        "total_checks": total_checks,
        "failures": len(failures),
        "maxima": maxima,
        "accounting": report["accounting"],
        "runtime_seconds": elapsed,
        "output": str(out_path),
    }, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
