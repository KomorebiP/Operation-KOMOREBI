#!/usr/bin/env python3
"""Generate independent concrete Lean checks for Block 08."""
from __future__ import annotations

from pathlib import Path

PRIMES = (2, 3, 5, 7, 11, 13)
R_VALUES = (1, 2, 3, 4, 5, 8, 13, 21, 34, 55, 89, 120, 180, 240)
H_VALUES = (0, 2, 5)
SPECIAL = (
    (2, 63, 0),
    (2, 240, 0),
    (3, 173, 1),
    (5, 191, 3),
    (7, 210, 4),
    (11, 219, 7),
    (13, 240, 8),
)


def vp_factorial(n: int, p: int) -> int:
    out = 0
    while n:
        n //= p
        out += n
    return out


def vp_binom(n: int, k: int, p: int) -> int:
    return vp_factorial(n, p) - vp_factorial(k, p) - vp_factorial(n - k, p)


def coarse_k(r: int, h: int) -> int:
    return max(r - 1, 0) // (h + 1)


def suffix_result(p: int, h: int, q_bound: int) -> tuple[int, int]:
    a_max = (q_bound - 1) // p
    def representative(a: int) -> int:
        return min(q_bound, p * (a + 1))
    def visible(a: int) -> int:
        return (p * q_bound - representative(a)) * (h + 1)
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


def target(p: int, r: int, h: int, q_bound: int, t: int) -> bool:
    if t <= 0:
        return False
    for q in range(1, min(q_bound, t) + 1):
        k = t - q
        if k * (h + 1) + vp_binom(t - 1, k, p) < r:
            return True
    return False


def compile_case(p: int, r: int, h: int) -> tuple[int, int, int, int, int, int, int, int]:
    bound = coarse_k(r, h) // (p - 1) + 1
    reps = 0
    q_star = None
    for q in range(1, bound + 1):
        cost, tested = suffix_result(p, h, q)
        reps += tested
        if cost >= r:
            q_star = q
            break
    assert q_star is not None
    lo = max(1, p * (q_star - 1))
    hi = p * q_star - 1
    full_targets = [t for t in range(lo, hi + 1) if target(p, r, h, q_star, t)]
    layer = max(full_targets)
    boundary_tests = hi - layer + 1
    return q_star, layer, q_star, boundary_tests, reps, lo, hi, hi + 1 - lo


def bool_lit(v: bool) -> str:
    return "true" if v else "false"


def main() -> None:
    here = Path(__file__).resolve().parent
    out = here / "LeanBoundaryVector.lean"
    cases = [(p, r, h) for p in PRIMES for r in R_VALUES for h in H_VALUES]
    for case in SPECIAL:
        if case not in cases:
            cases.append(case)

    lines = [
        "import KomorebiPadic.MaximumLayerCompiler",
        "",
        "open KomorebiPadic",
        "",
        "/-! Independently generated kernel checks for Block 08. -/",
        "",
        "/-! Optimized complete-compiler vectors. -/",
        "",
    ]
    for p, r, h in cases:
        q, layer, qtests, btests, reps, lo, hi, full = compile_case(p, r, h)
        lines.append(
            f"example : maximumLayerCompiler {p} {r} {h} = "
            f"⟨{q}, {layer}, {qtests}, {btests}, {reps}⟩ := by native_decide"
        )
        lines.append(
            f"example : finalFiberBoundaryResult {p} {r} {h} = "
            f"⟨{layer}, {btests}⟩ := by native_decide"
        )
        lines.append(
            f"example : finalFiberBoundaryLayer {p} {r} {h} = "
            f"exactMaximumLayer {p} {r} {h} := by native_decide"
        )
        lines.append(
            f"example : finalFiberTestCount {p} {r} {h} = {full} := by native_decide"
        )

    lines.extend(["", "/-! Generic descending-search vectors. -/", ""])
    patterns = (
        ([True], 9),
        ([True, False], 9),
        ([True, False, False, False], 9),
        ([True, False, True, False], 9),
        ([True, True, False, False, False], 9),
        ([True, False, False, True, False, False], 9),
        ([True, True, True, True, True, True], 9),
    )
    for values, lower in patterns:
        upper = lower + len(values) - 1
        highest = max(lower + i for i, b in enumerate(values) if b)
        tested = upper - highest + 1
        body = " | ".join(f"{lower+i} => {bool_lit(b)}" for i, b in enumerate(values))
        pred = f"(fun n => match n with | {body} | _ => false)"
        lines.append(
            f"example : firstTrueDescendingAux {pred} {upper} {len(values)} = "
            f"⟨{highest}, {tested}⟩ := by native_decide"
        )

    lines.extend(["", "/-! Boundary/exterior target checks. -/", ""])
    for p, r, h in SPECIAL:
        q, layer, _qt, btests, _reps, lo, hi, _full = compile_case(p, r, h)
        points = sorted({lo, layer, hi, max(lo, layer + 1), hi + 1})
        for t in points:
            lines.append(
                f"example : targetCompiler {p} {r} {h} {q} {t} = "
                f"{bool_lit(target(p, r, h, q, t))} := by native_decide"
            )
        lines.append(
            f"example : finalFiberBoundaryTestCount {p} {r} {h} = {btests} := by native_decide"
        )

    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote={out}")
    print(f"compiler_cases={len(cases)} generated_examples={sum(1 for x in lines if x.startswith('example :'))}")


if __name__ == "__main__":
    main()
