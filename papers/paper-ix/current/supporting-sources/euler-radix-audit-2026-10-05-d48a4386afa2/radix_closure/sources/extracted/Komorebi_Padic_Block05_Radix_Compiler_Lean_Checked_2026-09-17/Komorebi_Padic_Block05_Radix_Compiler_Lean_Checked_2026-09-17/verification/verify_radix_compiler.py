#!/usr/bin/env python3
"""Independent exact audit for Komorebi p-adic Block 05.

This verifies finite arithmetic surrogates only.  Universal correctness is
provided separately by the Lean theorems.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
DIRECT_Q_MAX = 200
COMB_Q_MAX = 45
REP_Q_MAX = 300
H_VALUES = tuple(range(9))
DIGIT_A_MAX = 600


def digit_sum(n: int, p: int) -> int:
    assert p >= 2 and n >= 0
    total = 0
    while n:
        n, d = divmod(n, p)
        total += d
    return total


def vp_int(n: int, p: int) -> int:
    assert n > 0 and p >= 2
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def vp_factorial(n: int, p: int) -> int:
    total = 0
    while n:
        n //= p
        total += n
    return total


def vp_binom_factorial(n: int, k: int, p: int) -> int:
    assert 0 <= k <= n
    return vp_factorial(n, p) - vp_factorial(k, p) - vp_factorial(n - k, p)


def vp_binom_integer(n: int, k: int, p: int) -> int:
    return vp_int(math.comb(n, k), p)


def kummer_carries(n: int, k: int, p: int) -> int:
    """Carries when k and n-k are added in base p."""
    assert 0 <= k <= n
    x, y = k, n - k
    carry = 0
    count = 0
    while x or y or carry:
        x, dx = divmod(x, p)
        y, dy = divmod(y, p)
        s = dx + dy + carry
        carry = 1 if s >= p else 0
        count += carry
    return count


def barrier_carry(p: int, Q: int, q: int) -> int:
    return vp_binom_factorial(p * Q - 1, p * Q - q, p)


def descended_carry(p: int, Q: int, q: int) -> int:
    return vp_binom_factorial(Q - 1, (q - 1) // p, p)


def representative(p: int, Q: int, a: int) -> int:
    return min(Q, p * (a + 1))


def branch_cost(p: int, h: int, Q: int, q: int) -> int:
    return (p * Q - q) * (h + 1) + barrier_carry(p, Q, q)


def radix_cost(p: int, h: int, Q: int, a: int) -> int:
    q = representative(p, Q, a)
    return (p * Q - q) * (h + 1) + vp_binom_factorial(Q - 1, a, p)


@dataclass
class AuditCounts:
    digit_append: int = 0
    top_digit: int = 0
    complement_digit: int = 0
    radix_factorial: int = 0
    radix_kummer: int = 0
    radix_integer: int = 0
    representative_shape: int = 0
    representative_carry: int = 0
    block_cost_monotonicity: int = 0
    minimum_equivalence: int = 0
    crossing_equivalence: int = 0


def main() -> int:
    start = time.perf_counter()
    counts = AuditCounts()
    failures: list[dict[str, object]] = []

    def check(name: str, condition: bool, **data: object) -> None:
        if not condition and len(failures) < 100:
            failures.append({"check": name, **data})

    # Low-digit append and top-barrier digit decompositions.
    for p in PRIMES:
        for a in range(DIGIT_A_MAX + 1):
            for b in range(p):
                counts.digit_append += 1
                check(
                    "digit_append",
                    digit_sum(b + p * a, p) == b + digit_sum(a, p),
                    p=p,
                    a=a,
                    b=b,
                )
        for Q in range(1, DIRECT_Q_MAX + 1):
            counts.top_digit += 1
            check(
                "top_digit",
                digit_sum(p * Q - 1, p) == (p - 1) + digit_sum(Q - 1, p),
                p=p,
                Q=Q,
            )

    # Kummer descent, checked using three exact implementations where feasible.
    for p in PRIMES:
        for Q in range(1, DIRECT_Q_MAX + 1):
            n = p * Q - 1
            for q in range(1, Q + 1):
                a, b = divmod(q - 1, p)
                comp = p * Q - q
                counts.complement_digit += 1
                check(
                    "complement_digit",
                    comp == (p - 1 - b) + p * (Q - 1 - a),
                    p=p,
                    Q=Q,
                    q=q,
                    a=a,
                    b=b,
                )
                lhs = vp_binom_factorial(n, comp, p)
                rhs = vp_binom_factorial(Q - 1, a, p)
                counts.radix_factorial += 1
                check("radix_factorial", lhs == rhs, p=p, Q=Q, q=q, lhs=lhs, rhs=rhs)

                lhs_c = kummer_carries(n, comp, p)
                rhs_c = kummer_carries(Q - 1, a, p)
                counts.radix_kummer += 1
                check(
                    "radix_kummer",
                    lhs_c == rhs_c == lhs,
                    p=p,
                    Q=Q,
                    q=q,
                    lhs=lhs,
                    lhs_c=lhs_c,
                    rhs_c=rhs_c,
                )

                if Q <= COMB_Q_MAX:
                    lhs_i = vp_binom_integer(n, comp, p)
                    rhs_i = vp_binom_integer(Q - 1, a, p)
                    counts.radix_integer += 1
                    check(
                        "radix_integer",
                        lhs_i == rhs_i == lhs,
                        p=p,
                        Q=Q,
                        q=q,
                        lhs_i=lhs_i,
                        rhs_i=rhs_i,
                    )

    # Exact representative and minimum compiler versus the full q scan.
    for p in PRIMES:
        for Q in range(1, REP_Q_MAX + 1):
            amax = (Q - 1) // p
            reps = [representative(p, Q, a) for a in range(amax + 1)]
            for a, qrep in enumerate(reps):
                counts.representative_shape += 1
                check(
                    "representative_shape",
                    p * a < qrep <= min(Q, p * (a + 1)) and (qrep - 1) // p == a,
                    p=p,
                    Q=Q,
                    a=a,
                    qrep=qrep,
                )
                bc = barrier_carry(p, Q, qrep)
                rc = vp_binom_factorial(Q - 1, a, p)
                counts.representative_carry += 1
                check(
                    "representative_carry",
                    bc == rc,
                    p=p,
                    Q=Q,
                    a=a,
                    qrep=qrep,
                    bc=bc,
                    rc=rc,
                )

                # The representative is the maximum q in its block and hence
                # minimizes every nonnegative visible-order coefficient.
                qlo = p * a + 1
                qhi = qrep
                for q in range(qlo, qhi + 1):
                    counts.block_cost_monotonicity += 1
                    for h in (0, 2, 8):
                        check(
                            "block_cost_monotonicity",
                            branch_cost(p, h, Q, qrep) <= branch_cost(p, h, Q, q),
                            p=p,
                            Q=Q,
                            a=a,
                            h=h,
                            q=q,
                            qrep=qrep,
                        )

            q_carries = [barrier_carry(p, Q, q) for q in range(1, Q + 1)]
            rep_carries = [vp_binom_factorial(Q - 1, a, p) for a in range(amax + 1)]
            for h in H_VALUES:
                brute = min((p * Q - q) * (h + 1) + q_carries[q - 1] for q in range(1, Q + 1))
                compressed = min(
                    (p * Q - reps[a]) * (h + 1) + rep_carries[a]
                    for a in range(amax + 1)
                )
                counts.minimum_equivalence += 1
                check(
                    "minimum_equivalence",
                    brute == compressed,
                    p=p,
                    Q=Q,
                    h=h,
                    brute=brute,
                    compressed=compressed,
                )
                for r in sorted({0, brute, brute + 1, brute + 2}):
                    full_crosses = any(
                        (p * Q - q) * (h + 1) + q_carries[q - 1] < r
                        for q in range(1, Q + 1)
                    )
                    compiled_crosses = compressed < r
                    counts.crossing_equivalence += 1
                    check(
                        "crossing_equivalence",
                        full_crosses == compiled_crosses,
                        p=p,
                        Q=Q,
                        h=h,
                        r=r,
                        brute=brute,
                        compressed=compressed,
                    )

    script_path = Path(__file__).resolve()
    result = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "claim_scope": (
            "Finite exact audit of digit decompositions, Kummer radix descent, "
            "one-representative-per-block compression, and minimum/crossing equivalence."
        ),
        "non_claims": [
            "Finite computation is not a universal proof.",
            "Universal statements are established only by the separately compiled Lean modules.",
        ],
        "arithmetic": "exact Python integers only",
        "parameters": {
            "primes": list(PRIMES),
            "direct_Q_max": DIRECT_Q_MAX,
            "integer_binomial_Q_max": COMB_Q_MAX,
            "representative_Q_max": REP_Q_MAX,
            "h_values": list(H_VALUES),
            "digit_a_max": DIGIT_A_MAX,
        },
        "counts": asdict(counts),
        "total_checks": sum(asdict(counts).values()),
        "failures": failures,
        "runtime_seconds": time.perf_counter() - start,
        "python_version": sys.version,
        "platform": platform.platform(),
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
    }
    out = script_path.parent.parent / "results" / "radix_compiler_audit.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
