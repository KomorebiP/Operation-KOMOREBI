#!/usr/bin/env python3
"""Generate bounded concrete Lean check chunks for Block 09 complexity fields."""
from __future__ import annotations
from pathlib import Path
from verify_final_fiber_boundary import PRIMES, concrete_boundary, quotient_bound
from verify_compiler_complexity import representative_budget
R_VALUES = (1, 2, 3, 4, 5, 8, 13, 21, 34, 55, 89, 144)
H_VALUES = (0, 1, 3, 7)
SPECIAL = ((3, 500, 0), (13, 300, 2))
CHUNK_CASES = 12

def case_lines(p: int, r: int, h: int) -> list[str]:
    result = concrete_boundary(p, r, h)
    B = quotient_bound(p, r, h)
    budget = representative_budget(p, B)
    total = result["quotient"] + result["boundary_tests"] + result["representative_tests"]
    budget_bound = B + p + budget
    closed_bound = B * B + B + p
    return [
        f"example : maximumLayerCompilerTotalTests {p} {r} {h} = {total} := by native_decide",
        f"example : radixRepresentativeBudget {p} {B} = {budget} := by native_decide",
        f"example : maximumLayerCompilerBudgetBound {p} {r} {h} = {budget_bound} := by native_decide",
        f"example : maximumLayerCompilerTestBound {p} {r} {h} = {closed_bound} := by native_decide",
        f"example : maximumLayerCompilerTotalTests {p} {r} {h} ≤ maximumLayerCompilerBudgetBound {p} {r} {h} := by native_decide",
        f"example : maximumLayerCompilerBudgetBound {p} {r} {h} ≤ maximumLayerCompilerTestBound {p} {r} {h} := by native_decide",
        f"example : (maximumLayerCompilerComplexityCertificate {p} {r} {h} (by decide) (by decide)).totalTests = {total} := by native_decide",
    ]

def main() -> None:
    here = Path(__file__).resolve().parent
    for old in here.glob("LeanComplexityVector_*.lean"):
        old.unlink()
    cases = [(p, r, h) for p in PRIMES for r in R_VALUES for h in H_VALUES]
    for case in SPECIAL:
        if case not in cases:
            cases.append(case)
    chunks = [cases[i:i+CHUNK_CASES] for i in range(0, len(cases), CHUNK_CASES)]
    total_examples = 0
    for idx, chunk in enumerate(chunks, 1):
        lines = [
            "import KomorebiPadic.CompilerComplexity", "", "open KomorebiPadic", "",
            f"/-! Independently generated Block 09 kernel checks, chunk {idx}/{len(chunks)}. -/", "",
        ]
        for p, r, h in chunk:
            lines.extend(case_lines(p, r, h))
        lines.append("")
        out = here / f"LeanComplexityVector_{idx:02d}.lean"
        out.write_text("\n".join(lines), encoding="utf-8")
        total_examples += sum(line.startswith("example :") for line in lines)
    # Retain a small umbrella file only as an index; do not compile all chunks in one process.
    index = here / "LeanComplexityVector.lean"
    index.write_text("/-! Block 09 complexity vectors are split into LeanComplexityVector_*.lean. -/\n", encoding="utf-8")
    print(f"cases={len(cases)} chunks={len(chunks)} examples={total_examples}")

if __name__ == "__main__":
    main()
