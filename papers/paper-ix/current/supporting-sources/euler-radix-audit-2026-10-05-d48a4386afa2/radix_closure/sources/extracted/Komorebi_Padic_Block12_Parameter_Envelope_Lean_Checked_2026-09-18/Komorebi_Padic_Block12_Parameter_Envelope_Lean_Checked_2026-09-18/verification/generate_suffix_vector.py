#!/usr/bin/env python3
"""Generate independent concrete Lean checks for Block 06.

The expected values are computed with Python arbitrary-precision integers from
factorial valuations and an independently written descending suffix scan.
"""
from __future__ import annotations

from pathlib import Path

PRIMES = (2, 3, 5, 7, 11)
H_VALUES = (0, 2, 8)
Q_VALUES = (1, 2, 3, 5, 8, 13, 32, 64, 128)
SPECIAL = ((2, 0, 7), (2, 0, 59), (2, 0, 251), (2, 0, 1915))


def vp_factorial(n: int, p: int) -> int:
    total = 0
    while n:
        n //= p
        total += n
    return total


def vp_binom(n: int, k: int, p: int) -> int:
    assert 0 <= k <= n
    return vp_factorial(n, p) - vp_factorial(k, p) - vp_factorial(n - k, p)


def representative(p: int, q_bound: int, a: int) -> int:
    return min(q_bound, p * (a + 1))


def visible(p: int, h: int, q_bound: int, a: int) -> int:
    return (p * q_bound - representative(p, q_bound, a)) * (h + 1)


def cost(p: int, h: int, q_bound: int, a: int) -> int:
    return visible(p, h, q_bound, a) + vp_binom(q_bound - 1, a, p)


def suffix_result(p: int, h: int, q_bound: int) -> tuple[int, int]:
    a_max = (q_bound - 1) // p
    best = cost(p, h, q_bound, a_max)
    tested = 1
    for a in range(a_max - 1, -1, -1):
        if best <= visible(p, h, q_bound, a):
            break
        best = min(best, cost(p, h, q_bound, a))
        tested += 1
    return best, tested


def main() -> None:
    here = Path(__file__).resolve().parent
    out = here / "LeanSuffixWindowVector.lean"
    cases = [(p, h, q) for p in PRIMES for h in H_VALUES for q in Q_VALUES]
    for case in SPECIAL:
        if case not in cases:
            cases.append(case)

    lines = [
        "import KomorebiPadic.SuffixWindow",
        "",
        "open KomorebiPadic",
        "",
        "/-! Independently generated concrete kernel checks for the Block 06 suffix compiler. -/",
        "",
    ]
    for p, h, q_bound in cases:
        best, tested = suffix_result(p, h, q_bound)
        lines.append(
            f"example : suffixRadixBarrierResult {p} {h} {q_bound} = "
            f"⟨{best}, {tested}⟩ := by native_decide"
        )
    lines.extend(["", "/-! Threshold reflection immediately below and above selected exact minima. -/", ""])
    threshold_cases = [
        (2, 0, 7),
        (2, 0, 59),
        (2, 0, 251),
        (2, 0, 1915),
        (3, 0, 13),
        (3, 2, 64),
        (5, 8, 128),
        (7, 0, 64),
        (11, 2, 128),
    ]
    for p, h, q_bound in threshold_cases:
        best, _ = suffix_result(p, h, q_bound)
        lines.append(
            f"example : suffixCompilerCrosses {p} {best} {h} {q_bound} = false := by native_decide"
        )
        lines.append(
            f"example : suffixCompilerCrosses {p} {best + 1} {h} {q_bound} = true := by native_decide"
        )
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")
    print(f"result_cases={len(cases)} threshold_checks={2 * len(threshold_cases)} total={len(cases) + 2 * len(threshold_cases)}")


if __name__ == "__main__":
    main()
