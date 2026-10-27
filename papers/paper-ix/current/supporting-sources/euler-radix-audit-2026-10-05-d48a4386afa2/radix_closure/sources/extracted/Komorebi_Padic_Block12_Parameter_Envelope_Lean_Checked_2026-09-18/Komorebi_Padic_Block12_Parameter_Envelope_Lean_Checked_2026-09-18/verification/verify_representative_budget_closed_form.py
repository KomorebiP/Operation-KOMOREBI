#!/usr/bin/env python3
"""Independent exact finite audit for Komorebi p-adic Block 10.

The universal closed-form identity is proved in Lean. This script independently
checks the executable finite sum, the quotient/remainder formula, the final
radix-block formula, all totalized boundary conventions, and the resulting
closed compiler envelope on a broad finite domain.
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

BASE_MAX = 160
ENDPOINT_MAX = 40_000
COMPILER_PRIMES = (2, 3, 5, 7, 11, 13)
COMPILER_R_MAX = 150
COMPILER_H_VALUES = tuple(range(10))
STRESS_BUDGET_CASES = (
    (0, 0), (0, 1), (0, 10**6),
    (1, 0), (1, 1), (1, 10**6),
    (2, 10**6), (3, 999_983), (16, 1_000_003),
    (97, 10**7 + 19), (160, 10**8 + 7),
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


def qr_form(p: int, B: int) -> int:
    q = nat_div(B, p)
    r = nat_mod(B, p)
    return B + p * choose2(q) + q * r


def last_block_data(p: int, B: int) -> tuple[int, int]:
    pred = max(B - 1, 0)
    return nat_div(pred, p), nat_mod(pred, p)


def last_choose_form(p: int, B: int) -> int:
    d, s = last_block_data(p, B)
    return B + p * choose2(d) + d * (s + 1)


def closed_form(p: int, B: int) -> int:
    d, s = last_block_data(p, B)
    return B + (p * d * (d - 1)) // 2 + d * (s + 1)


def representative_budget_direct(p: int, B: int) -> int:
    return sum(nat_div(Q - 1, p) + 1 for Q in range(1, B + 1))


def closed_compiler_bound(p: int, r: int, h: int) -> int:
    B = quotient_bound(p, r, h)
    d, s = last_block_data(p, B)
    return 2 * B + p + (p * d * (d - 1)) // 2 + d * (s + 1)


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
        "budget": {"value": 0, "case": None},
        "closed_compiler_bound": {"value": 0, "case": None},
        "closed_bound_slack": {"value": 0, "case": None},
    }

    def check(name: str, condition: bool, **data: object) -> None:
        counts[name] += 1
        if not condition and len(failures) < 200:
            failures.append({"check": name, **data})

    def record_max(name: str, value: int, case: dict[str, int]) -> None:
        if value > int(maxima[name]["value"]):
            maxima[name] = {"value": value, "case": case}

    # Exhaustive rectangular audit. The direct finite sum is maintained by its
    # defining recurrence, independently from either closed form.
    for p in range(BASE_MAX + 1):
        running = 0
        previous = 0
        for B in range(ENDPOINT_MAX + 1):
            if B > 0:
                running += nat_div(B - 1, p) + 1
            qf = qr_form(p, B)
            lf = last_choose_form(p, B)
            cf = closed_form(p, B)
            case = {"p": p, "B": B}
            check("direct_eq_qr", running == qf, **case, direct=running, qr=qf)
            check("qr_eq_last_choose", qf == lf, **case, qr=qf, last=lf)
            check("last_choose_eq_closed", lf == cf, **case, last=lf, closed=cf)
            check("direct_eq_closed", running == cf, **case, direct=running, closed=cf)
            if B == 0:
                check("zero_endpoint", running == 0, **case)
            else:
                check(
                    "successor_recurrence",
                    running == previous + nat_div(B - 1, p) + 1,
                    **case,
                    current=running,
                    previous=previous,
                )
            if p == 0:
                check("zero_base", running == B, **case, direct=running)
            if p == 1:
                check("one_base", running == B * (B + 1) // 2, **case, direct=running)
            previous = running
            record_max("budget", running, case)

    # Larger endpoints, using a literal finite sum where still proportionate.
    stress_budget_records: list[dict[str, int]] = []
    for p, B in STRESS_BUDGET_CASES:
        if B <= 1_000_000:
            direct = representative_budget_direct(p, B)
        else:
            # Independent block enumeration, one term per quotient block.
            direct = 0
            if p == 0:
                direct = B
            else:
                remaining = B
                quotient = 0
                while remaining:
                    width = min(p, remaining)
                    direct += width * (quotient + 1)
                    remaining -= width
                    quotient += 1
        qf = qr_form(p, B)
        lf = last_choose_form(p, B)
        cf = closed_form(p, B)
        check("stress_direct_eq_qr", direct == qf, p=p, B=B)
        check("stress_qr_eq_last", qf == lf, p=p, B=B)
        check("stress_last_eq_closed", lf == cf, p=p, B=B)
        stress_budget_records.append({"p": p, "B": B, "budget": direct})

    # Connect the closed formula to the exact compiler counters on a finite
    # prime-base grid and on the retained large stress cases.
    compiler_records: list[dict[str, int]] = []

    def audit_compiler_case(p: int, r: int, h: int, lane: str) -> None:
        case = {"p": p, "r": r, "h": h}
        out = concrete_boundary(p, r, h)
        exact_total = out["quotient"] + out["boundary_tests"] + out["representative_tests"]
        B = quotient_bound(p, r, h)
        direct_budget = representative_budget_direct(p, B)
        old_bound = B + p + direct_budget
        new_bound = closed_compiler_bound(p, r, h)
        counts[f"{lane}_compiler_cases"] += 1
        check("compiler_budget_closed_identity", old_bound == new_bound, lane=lane, **case)
        check("compiler_total_le_closed", exact_total <= new_bound, lane=lane, **case)
        check("compiler_budget_formula", direct_budget == closed_form(p, B), lane=lane, **case)
        record_max("closed_compiler_bound", new_bound, case)
        record_max("closed_bound_slack", new_bound - exact_total, case)
        if lane == "stress":
            compiler_records.append({
                **case,
                "quotient": out["quotient"],
                "layer": out["layer"],
                "exact_total": exact_total,
                "quotient_bound": B,
                "representative_budget": direct_budget,
                "closed_bound": new_bound,
            })

    for p in COMPILER_PRIMES:
        for r in range(1, COMPILER_R_MAX + 1):
            for h in COMPILER_H_VALUES:
                audit_compiler_case(p, r, h, "grid")
    for args in COMPILER_STRESS_CASES:
        audit_compiler_case(*args, lane="stress")

    source_paths = sorted((root / "lean" / "KomorebiPadic").glob("*.lean"))
    report = {
        "schema": "komorebi-padic-block10-closed-budget-audit-v1",
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
        "compiler_stress_records": compiler_records,
        "source_sha256": {str(p.relative_to(root)): sha256(p) for p in source_paths},
        "runtime_seconds": time.perf_counter() - started,
        "platform": platform.platform(),
        "python": sys.version,
        "non_claims": [
            "Finite audit output is not the universal proof.",
            "The closed compiler envelope is an upper bound, not the exact operation count.",
            "No asymptotic optimality or novelty claim is made.",
        ],
    }
    out_path = root / "results" / "representative_budget_closed_form_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
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
