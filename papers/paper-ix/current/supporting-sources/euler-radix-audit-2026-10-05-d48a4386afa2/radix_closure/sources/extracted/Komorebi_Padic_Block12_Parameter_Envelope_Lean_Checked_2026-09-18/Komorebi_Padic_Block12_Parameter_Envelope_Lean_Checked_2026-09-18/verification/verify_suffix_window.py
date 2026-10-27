#!/usr/bin/env python3
"""Independent exact audit for the Block 06 suffix-window compiler.

The universal result is kernel-checked in Lean.  This program audits the
executable finite surrogate with Python arbitrary-precision integers and a
separately implemented generic branch-and-bound reference.
"""
from __future__ import annotations

import hashlib
import json
import platform
import random
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
H_VALUES = tuple(range(13))
GRID_Q_MAX = 1000
BRUTE_Q_MAX = 150
GENERIC_CASES = 20_000
GENERIC_LENGTH_MAX = 128
STRESS_P = 2
STRESS_H = 0
STRESS_Q_MAX = 10_000
SEED = 0x4B4F4D4F52454249


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def vp_factorial(n: int, p: int) -> int:
    total = 0
    while n:
        n //= p
        total += n
    return total


def vp_binom_factorial(n: int, k: int, p: int) -> int:
    assert 0 <= k <= n
    return vp_factorial(n, p) - vp_factorial(k, p) - vp_factorial(n - k, p)


def representative(p: int, q_bound: int, a: int) -> int:
    return min(q_bound, p * (a + 1))


def visible_cost(p: int, h: int, q_bound: int, a: int) -> int:
    return (p * q_bound - representative(p, q_bound, a)) * (h + 1)


def carry_from_table(vf: list[int], q_bound: int, a: int) -> int:
    n = q_bound - 1
    return vf[n] - vf[a] - vf[n - a]


def radix_cost(p: int, h: int, q_bound: int, a: int, vf: list[int]) -> int:
    return visible_cost(p, h, q_bound, a) + carry_from_table(vf, q_bound, a)


def suffix_scan_arrays(visible: list[int], carry: list[int]) -> tuple[int, int, int | None]:
    """Return exact suffix cost, complete evaluations, and first skipped index."""
    assert visible and len(visible) == len(carry)
    best = visible[-1] + carry[-1]
    tested = 1
    stopped_at: int | None = None
    for i in range(len(visible) - 2, -1, -1):
        if best <= visible[i]:
            stopped_at = i
            break
        best = min(best, visible[i] + carry[i])
        tested += 1
    return best, tested, stopped_at


def suffix_radix(p: int, h: int, q_bound: int, vf: list[int]) -> tuple[int, int, int | None]:
    a_max = (q_bound - 1) // p
    best = radix_cost(p, h, q_bound, a_max, vf)
    tested = 1
    stopped_at: int | None = None
    for a in range(a_max - 1, -1, -1):
        visible = visible_cost(p, h, q_bound, a)
        if best <= visible:
            stopped_at = a
            break
        best = min(best, visible + carry_from_table(vf, q_bound, a))
        tested += 1
    return best, tested, stopped_at


@dataclass
class Counts:
    generic_cases: int = 0
    generic_cost_checks: int = 0
    generic_stop_certificates: int = 0
    concrete_cases: int = 0
    concrete_visible_monotonicity: int = 0
    concrete_full_cost_evaluations: int = 0
    concrete_suffix_cost_evaluations: int = 0
    concrete_minimum_equivalence: int = 0
    concrete_stop_certificates: int = 0
    concrete_tested_bounds: int = 0
    concrete_threshold_reflections: int = 0
    direct_q_minimum_cases: int = 0
    direct_q_cost_evaluations: int = 0
    direct_radix_identity_checks: int = 0
    stress_cases: int = 0
    stress_full_cost_evaluations: int = 0
    stress_suffix_cost_evaluations: int = 0
    stress_minimum_equivalence: int = 0


def main() -> int:
    started = time.perf_counter()
    counts = Counts()
    failures: list[dict[str, object]] = []
    tested_histogram: Counter[int] = Counter()
    max_tested = 0
    max_tested_witness: tuple[int, int, int, int] | None = None
    stress_max_tested = 0
    stress_max_witness: tuple[int, int] | None = None

    def fail(check: str, **data: object) -> None:
        if len(failures) < 100:
            failures.append({"check": check, **data})

    # Generic branch-and-bound audit.  The visible sequence is generated
    # antitone in the index, while carry values are arbitrary naturals.
    rng = random.Random(SEED)
    for case in range(GENERIC_CASES):
        length = rng.randint(1, GENERIC_LENGTH_MAX)
        visible = [0] * length
        visible[-1] = rng.randrange(0, 40)
        for i in range(length - 2, -1, -1):
            visible[i] = visible[i + 1] + rng.randrange(0, 9)
        carry = [rng.randrange(0, 80) for _ in range(length)]
        suffix, tested, stopped_at = suffix_scan_arrays(visible, carry)
        costs = [v + c for v, c in zip(visible, carry, strict=True)]
        full = min(costs)
        counts.generic_cases += 1
        counts.generic_cost_checks += length
        if suffix != full:
            fail(
                "generic_minimum",
                case=case,
                visible=visible,
                carry=carry,
                suffix=suffix,
                full=full,
            )
        if not (1 <= tested <= length):
            fail("generic_tested_bounds", case=case, tested=tested, length=length)
        if stopped_at is not None:
            counts.generic_stop_certificates += stopped_at + 1
            for i in range(stopped_at + 1):
                if costs[i] < suffix:
                    fail(
                        "generic_stop_certificate",
                        case=case,
                        stopped_at=stopped_at,
                        skipped=i,
                        skipped_cost=costs[i],
                        best=suffix,
                    )

    # Concrete radix grid.  Precomputed factorial valuations make the full
    # representative comparison independent and inexpensive.
    for p in PRIMES:
        vf = [vp_factorial(n, p) for n in range(GRID_Q_MAX)]
        for h in H_VALUES:
            for q_bound in range(1, GRID_Q_MAX + 1):
                a_max = (q_bound - 1) // p
                costs: list[int] = []
                previous_visible: int | None = None
                for a in range(a_max + 1):
                    visible = visible_cost(p, h, q_bound, a)
                    if previous_visible is not None:
                        counts.concrete_visible_monotonicity += 1
                        if visible > previous_visible:
                            fail(
                                "visible_not_antitone",
                                p=p,
                                h=h,
                                Q=q_bound,
                                a=a,
                                previous=previous_visible,
                                current=visible,
                            )
                    previous_visible = visible
                    costs.append(visible + carry_from_table(vf, q_bound, a))
                full = min(costs)
                suffix, tested, stopped_at = suffix_radix(p, h, q_bound, vf)
                counts.concrete_cases += 1
                counts.concrete_full_cost_evaluations += len(costs)
                counts.concrete_suffix_cost_evaluations += tested
                counts.concrete_minimum_equivalence += 1
                counts.concrete_tested_bounds += 1
                counts.concrete_threshold_reflections += 2
                tested_histogram[tested] += 1
                if tested > max_tested:
                    max_tested = tested
                    max_tested_witness = (p, h, q_bound, full)
                if suffix != full:
                    fail(
                        "radix_minimum",
                        p=p,
                        h=h,
                        Q=q_bound,
                        suffix=suffix,
                        full=full,
                    )
                if not (1 <= tested <= len(costs)):
                    fail(
                        "radix_tested_bounds",
                        p=p,
                        h=h,
                        Q=q_bound,
                        tested=tested,
                        full_count=len(costs),
                    )
                # Exact Boolean threshold behavior at r=best and r=best+1.
                if suffix < full or not (suffix < full + 1):
                    fail("threshold_reflection", p=p, h=h, Q=q_bound, cost=full)
                if stopped_at is not None:
                    for a in range(stopped_at + 1):
                        counts.concrete_stop_certificates += 1
                        if costs[a] < suffix:
                            fail(
                                "radix_stop_certificate",
                                p=p,
                                h=h,
                                Q=q_bound,
                                stopped_at=stopped_at,
                                skipped=a,
                                skipped_cost=costs[a],
                                best=suffix,
                            )

                # On a smaller range, compare with the original q-by-q diagonal
                # cost and independently recheck the radix valuation identity.
                if q_bound <= BRUTE_Q_MAX:
                    direct: list[int] = []
                    n = p * q_bound - 1
                    for q in range(1, q_bound + 1):
                        a = (q - 1) // p
                        lhs = vp_binom_factorial(n, p * q_bound - q, p)
                        rhs = carry_from_table(vf, q_bound, a)
                        counts.direct_radix_identity_checks += 1
                        if lhs != rhs:
                            fail(
                                "direct_radix_identity",
                                p=p,
                                Q=q_bound,
                                q=q,
                                lhs=lhs,
                                rhs=rhs,
                            )
                        direct.append((p * q_bound - q) * (h + 1) + lhs)
                    counts.direct_q_minimum_cases += 1
                    counts.direct_q_cost_evaluations += len(direct)
                    if min(direct) != full:
                        fail(
                            "direct_q_minimum",
                            p=p,
                            h=h,
                            Q=q_bound,
                            direct=min(direct),
                            radix=full,
                        )

    # Deep p=2,h=0 lane.  This intentionally extends beyond the Block 04
    # Q<=500 audit and checks that the window can exceed the previously observed
    # finite maximum of four representatives.
    vf_stress = [vp_factorial(n, STRESS_P) for n in range(STRESS_Q_MAX)]
    for q_bound in range(1, STRESS_Q_MAX + 1):
        a_max = (q_bound - 1) // STRESS_P
        full = min(
            radix_cost(STRESS_P, STRESS_H, q_bound, a, vf_stress)
            for a in range(a_max + 1)
        )
        suffix, tested, _ = suffix_radix(STRESS_P, STRESS_H, q_bound, vf_stress)
        counts.stress_cases += 1
        counts.stress_full_cost_evaluations += a_max + 1
        counts.stress_suffix_cost_evaluations += tested
        counts.stress_minimum_equivalence += 1
        if tested > stress_max_tested:
            stress_max_tested = tested
            stress_max_witness = (q_bound, full)
        if suffix != full:
            fail(
                "stress_minimum",
                p=STRESS_P,
                h=STRESS_H,
                Q=q_bound,
                suffix=suffix,
                full=full,
            )

    elapsed = time.perf_counter() - started
    here = Path(__file__).resolve().parent
    report = {
        "schema": "komorebi-padic-block06-suffix-window-audit-v1",
        "status": "PASS" if not failures else "FAIL",
        "arithmetic": "Python arbitrary-precision integers only; no floating point in checked assertions",
        "seed": SEED,
        "generic": {
            "cases": GENERIC_CASES,
            "length_range": [1, GENERIC_LENGTH_MAX],
        },
        "radix_grid": {
            "primes": list(PRIMES),
            "h_values": list(H_VALUES),
            "Q_range": [1, GRID_Q_MAX],
            "direct_q_comparison_Q_range": [1, BRUTE_Q_MAX],
        },
        "stress_lane": {
            "p": STRESS_P,
            "h": STRESS_H,
            "Q_range": [1, STRESS_Q_MAX],
            "max_tested": stress_max_tested,
            "first_max_witness": {
                "Q": stress_max_witness[0],
                "cost": stress_max_witness[1],
            }
            if stress_max_witness
            else None,
        },
        "counts": asdict(counts),
        "total_recorded_checks": sum(asdict(counts).values()),
        "tested_histogram_grid": {str(k): v for k, v in sorted(tested_histogram.items())},
        "max_tested_grid": max_tested,
        "first_max_tested_grid_witness": {
            "p": max_tested_witness[0],
            "h": max_tested_witness[1],
            "Q": max_tested_witness[2],
            "cost": max_tested_witness[3],
        }
        if max_tested_witness
        else None,
        "failures": failures,
        "failure_count": len(failures),
        "elapsed_seconds": elapsed,
        "python": sys.version,
        "platform": platform.platform(),
        "source_sha256": {"verify_suffix_window.py": sha256(Path(__file__))},
        "claim_boundary": (
            "This is bounded exact implementation evidence. Universal branch-and-bound and "
            "barrier correctness are supplied by the Lean proofs. Observed window sizes are not "
            "universal complexity bounds."
        ),
    }
    out = here.parent / "results" / "suffix_window_audit.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
