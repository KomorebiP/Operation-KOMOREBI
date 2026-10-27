#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"
CHUNK_SIZE = 160


def nat_div(n: int, p: int) -> int:
    return 0 if p == 0 else n // p


def nat_mod(n: int, p: int) -> int:
    return n if p == 0 else n % p


def closed_form(p: int, B: int) -> int:
    pred = max(B - 1, 0)
    d = nat_div(pred, p)
    s = nat_mod(pred, p)
    return B + (p * d * (d - 1)) // 2 + d * (s + 1)


def coarse_k(r: int, h: int) -> int:
    return max(r - 1, 0) // (h + 1)


def quotient_bound(p: int, r: int, h: int) -> int:
    return coarse_k(r, h) // max(p - 1, 0) + 1 if p != 1 else coarse_k(r, h) // 0 + 1


def closed_compiler_bound(p: int, r: int, h: int) -> int:
    B = quotient_bound(p, r, h)
    return B + p + closed_form(p, B)


def main() -> None:
    examples: list[str] = []
    for p in range(17):
        for B in range(65):
            expected = closed_form(p, B)
            examples.append(
                f"example : radixRepresentativeBudget {p} {B} = {expected} := by native_decide"
            )
            examples.append(
                f"example : radixRepresentativeBudgetClosedForm {p} {B} = {expected} := by native_decide"
            )

    primes = (2, 3, 5, 7, 11, 13)
    r_values = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
    h_values = (0, 1, 3)
    for p in primes:
        for r in r_values:
            for h in h_values:
                expected = closed_compiler_bound(p, r, h)
                examples.append(
                    f"example : maximumLayerCompilerClosedBudgetBound {p} {r} {h} = {expected} := by native_decide"
                )
                examples.append(
                    f"example : maximumLayerCompilerBudgetBound {p} {r} {h} = {expected} := by native_decide"
                )

    # Small executable certificate projections.
    cert_cases = ((2, 1, 0), (2, 8, 2), (3, 13, 1), (5, 21, 3), (7, 34, 1), (13, 55, 0))
    for p, r, h in cert_cases:
        B = quotient_bound(p, r, h)
        pred = max(B - 1, 0)
        d = nat_div(pred, p)
        s = nat_mod(pred, p)
        examples.append(
            f"example : (maximumLayerCompilerClosedFormCertificate {p} {r} {h} (by decide) (by decide)).quotientBound = {B} := by native_decide"
        )
        examples.append(
            f"example : (maximumLayerCompilerClosedFormCertificate {p} {r} {h} (by decide) (by decide)).blockQuotient = {d} := by native_decide"
        )
        examples.append(
            f"example : (maximumLayerCompilerClosedFormCertificate {p} {r} {h} (by decide) (by decide)).blockRemainder = {s} := by native_decide"
        )

    # Remove stale generated chunks.
    for path in OUT.glob("LeanClosedFormVector_*.lean"):
        path.unlink()
    chunks = [examples[i : i + CHUNK_SIZE] for i in range(0, len(examples), CHUNK_SIZE)]
    for idx, chunk in enumerate(chunks, start=1):
        path = OUT / f"LeanClosedFormVector_{idx:02d}.lean"
        lines = [
            "import KomorebiPadic.RepresentativeBudgetClosedForm",
            "",
            "open KomorebiPadic",
            "",
            f"/-! Independently generated Block 10 kernel checks, chunk {idx}/{len(chunks)}. -/",
            "",
            *chunk,
            "",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "results" / "closed_form_vector_count.txt").write_text(
        f"files={len(chunks)}\nexamples={len(examples)}\n", encoding="utf-8"
    )
    print(f"files={len(chunks)} examples={len(examples)}")


if __name__ == "__main__":
    main()
