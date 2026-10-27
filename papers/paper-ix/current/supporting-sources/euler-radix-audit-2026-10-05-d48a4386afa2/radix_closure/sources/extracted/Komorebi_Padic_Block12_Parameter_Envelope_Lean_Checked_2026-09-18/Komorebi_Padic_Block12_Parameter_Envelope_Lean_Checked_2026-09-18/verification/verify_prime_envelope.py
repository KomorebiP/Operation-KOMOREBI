#!/usr/bin/env python3
"""Independent exact finite audit for Komorebi p-adic Block 11.

The universal statements are proved in Lean. This script independently checks
finite instances of the representative-budget recurrence, the exact envelope
slack, the equality criterion, and the integrated compiler bounds using Python
arbitrary-precision integers.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

from verify_final_fiber_boundary import concrete_boundary, quotient_bound

BASE_MAX = 128
ENDPOINT_MAX = 30_000
COMPILER_PRIMES = (2, 3, 5, 7, 11, 13)
COMPILER_R_MAX = 120
COMPILER_H_VALUES = tuple(range(6))
STRESS_BUDGET_CASES = (
    (1, 10**6),
    (2, 10**7 + 19),
    (3, 10**8 + 7),
    (17, 10**9 + 33),
    (97, 10**10 + 123),
    (128, 10**12 + 39),
)
COMPILER_STRESS_CASES = (
    (2, 8059, 0),
    (2, 12000, 3),
    (3, 5000, 0),
    (5, 4000, 1),
    (7, 3500, 2),
    (13, 3000, 0),
)


def nat_div(n: int, p: int) -> int:
    return 0 if p == 0 else n // p


def nat_mod(n: int, p: int) -> int:
    return n if p == 0 else n % p


def choose2(n: int) -> int:
    return n * (n - 1) // 2


def last_block_data(p: int, B: int) -> tuple[int, int]:
    pred = max(B - 1, 0)
    return nat_div(pred, p), nat_mod(pred, p)


def closed_budget(p: int, B: int) -> int:
    d, s = last_block_data(p, B)
    return B + (p * d * (d - 1)) // 2 + d * (s + 1)


def prime_envelope(p: int, B: int) -> int:
    d, _ = last_block_data(p, B)
    return B + (p * d * (d + 1)) // 2


def prime_gap(p: int, B: int) -> int:
    d, s = last_block_data(p, B)
    return d * max(p - (s + 1), 0)


def representative_budget_direct(p: int, B: int) -> int:
    return sum(nat_div(Q - 1, p) + 1 for Q in range(1, B + 1))


def compiler_closed_bound(p: int, r: int, h: int) -> int:
    B = quotient_bound(p, r, h)
    return B + p + closed_budget(p, B)


def compiler_prime_bound(p: int, r: int, h: int) -> int:
    B = quotient_bound(p, r, h)
    return B + p + prime_envelope(p, B)


def compiler_gap(p: int, r: int, h: int) -> int:
    return prime_gap(p, quotient_bound(p, r, h))


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
        "gap": {"value": 0, "case": None},
        "relative_gap_ppm": {"value": 0, "case": None},
        "compiler_prime_bound": {"value": 0, "case": None},
        "compiler_prime_slack": {"value": 0, "case": None},
    }

    def check(name: str, condition: bool, **data: object) -> None:
        counts[name] += 1
        if not condition and len(failures) < 200:
            failures.append({"check": name, **data})

    def record_max(name: str, value: int, case: dict[str, int]) -> None:
        if value > int(maxima[name]["value"]):
            maxima[name] = {"value": value, "case": case}

    # Direct recurrence audit. The running total follows the defining finite
    # sum independently from both the closed formula and the new envelope.
    for p in range(BASE_MAX + 1):
        running = 0
        for B in range(ENDPOINT_MAX + 1):
            if B > 0:
                running += nat_div(B - 1, p) + 1
            d, s = last_block_data(p, B)
            closed = closed_budget(p, B)
            envelope = prime_envelope(p, B)
            gap = prime_gap(p, B)
            case = {"p": p, "B": B}
            check("direct_eq_closed", running == closed, **case)
            check("envelope_le_square", envelope <= B * B, **case)
            if p == 0:
                check("zero_base_budget", running == B, **case)
                continue
            check("remainder_cap", s + 1 <= p, **case, s=s)
            check("closed_plus_gap_eq_envelope", closed + gap == envelope, **case)
            check("direct_le_envelope", running <= envelope, **case)
            criterion = (d == 0 or s + 1 == p)
            check("equality_criterion", (running == envelope) == criterion, **case, d=d, s=s)
            check("choose_envelope", envelope == B + p * choose2(d + 1), **case)
            record_max("gap", gap, case)
            ppm = 0 if envelope == 0 else gap * 1_000_000 // envelope
            record_max("relative_gap_ppm", ppm, case)

    stress_budget_records: list[dict[str, int]] = []
    for p, B in STRESS_BUDGET_CASES:
        d, s = last_block_data(p, B)
        closed = closed_budget(p, B)
        envelope = prime_envelope(p, B)
        gap = prime_gap(p, B)
        block_enumeration = B + p * choose2(d) + d * (s + 1)
        check("stress_block_eq_closed", block_enumeration == closed, p=p, B=B)
        check("stress_closed_plus_gap", closed + gap == envelope, p=p, B=B)
        check("stress_envelope_square", envelope <= B * B, p=p, B=B)
        check("stress_equality_criterion", (closed == envelope) == (d == 0 or s + 1 == p), p=p, B=B)
        stress_budget_records.append({"p": p, "B": B, "d": d, "s": s, "closed": closed, "gap": gap, "envelope": envelope})

    compiler_stress_records: list[dict[str, int]] = []

    def audit_compiler_case(p: int, r: int, h: int, lane: str) -> None:
        case = {"p": p, "r": r, "h": h}
        out = concrete_boundary(p, r, h)
        exact_total = out["quotient"] + out["boundary_tests"] + out["representative_tests"]
        B = quotient_bound(p, r, h)
        direct_budget = representative_budget_direct(p, B)
        closed = compiler_closed_bound(p, r, h)
        envelope = compiler_prime_bound(p, r, h)
        gap = compiler_gap(p, r, h)
        quadratic = B * B + B + p
        counts[f"{lane}_compiler_cases"] += 1
        check("compiler_finite_sum_eq_closed", B + p + direct_budget == closed, lane=lane, **case)
        check("compiler_closed_plus_gap", closed + gap == envelope, lane=lane, **case)
        check("compiler_total_le_closed", exact_total <= closed, lane=lane, **case)
        check("compiler_total_le_envelope", exact_total <= envelope, lane=lane, **case)
        check("compiler_envelope_le_quadratic", envelope <= quadratic, lane=lane, **case)
        check("compiler_remainder_cap", last_block_data(p, B)[1] + 1 <= p, lane=lane, **case)
        record_max("compiler_prime_bound", envelope, case)
        record_max("compiler_prime_slack", envelope - exact_total, case)
        if lane == "stress":
            compiler_stress_records.append({
                **case,
                "quotient": out["quotient"],
                "layer": out["layer"],
                "exact_total": exact_total,
                "quotient_bound": B,
                "closed_bound": closed,
                "prime_envelope_gap": gap,
                "prime_envelope_bound": envelope,
                "quadratic_bound": quadratic,
            })

    for p in COMPILER_PRIMES:
        for r in range(1, COMPILER_R_MAX + 1):
            for h in COMPILER_H_VALUES:
                audit_compiler_case(p, r, h, "grid")
    for args in COMPILER_STRESS_CASES:
        audit_compiler_case(*args, lane="stress")

    source_paths = sorted((root / "lean" / "KomorebiPadic").glob("*.lean"))
    report = {
        "schema": "komorebi-padic-block11-prime-envelope-audit-v1",
        "status": "PASS" if not failures else "FAIL",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": {
            "base_range": [0, BASE_MAX],
            "endpoint_range": [0, ENDPOINT_MAX],
            "compiler_primes": list(COMPILER_PRIMES),
            "compiler_r_max": COMPILER_R_MAX,
            "compiler_h_values": list(COMPILER_H_VALUES),
            "stress_budget_cases": [list(x) for x in STRESS_BUDGET_CASES],
            "compiler_stress_cases": [list(x) for x in COMPILER_STRESS_CASES],
        },
        "counts": dict(sorted(counts.items())),
        "total_recorded_checks_and_cases": sum(counts.values()),
        "failure_count": len(failures),
        "failures": failures,
        "maxima": maxima,
        "stress_budget_records": stress_budget_records,
        "compiler_stress_records": compiler_stress_records,
        "source_sha256": {str(p.relative_to(root)): sha256(p) for p in source_paths},
        "runtime_seconds": time.perf_counter() - started,
        "platform": platform.platform(),
        "python": sys.version,
        "non_claims": [
            "Finite audit output is not the universal proof.",
            "The prime-sensitive envelope is an upper bound, not an exact operation count in general.",
            "No asymptotic optimality or novelty claim is made.",
            "The end-to-end compiler theorem remains restricted to prime bases and positive precision.",
        ],
    }
    out_path = root / "results" / "prime_envelope_audit.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "total_checks": report["total_recorded_checks_and_cases"],
        "failures": len(failures),
        "maxima": maxima,
        "runtime_seconds": report["runtime_seconds"],
        "output": str(out_path),
    }, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
