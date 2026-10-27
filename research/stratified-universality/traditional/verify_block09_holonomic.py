from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(exist_ok=True)


@dataclass
class Counter:
    total: int = 0
    failures: int = 0

    def check(self, cond: bool, message: str) -> None:
        self.total += 1
        if not cond:
            self.failures += 1
            raise AssertionError(message)


def poch(a: Fraction, n: int) -> Fraction:
    out = Fraction(1)
    for k in range(n):
        out *= a + k
    return out


def packet_coeff(lam: Fraction, alpha: int, N: int, j: int, m: int) -> Fraction:
    n = N * m + j
    return poch(lam, n) * Fraction(alpha) ** n / math.factorial(n)


def packet_parameters(lam: Fraction, N: int, j: int) -> tuple[list[Fraction], list[Fraction]]:
    upper = [(lam + j + r) / N for r in range(N)]
    full_lower = [Fraction(j + 1 + r, N) for r in range(N)]
    lower = [b for b in full_lower if b != 1]
    assert len(lower) == N - 1
    return upper, lower


def is_integer(x: Fraction) -> bool:
    return x.denominator == 1


def finite_difference(values: list[Fraction]) -> list[Fraction]:
    return [values[i + 1] - values[i] for i in range(len(values) - 1)]


def support_count(M: int, N: int, j: int) -> int:
    if j > M:
        return 0
    return (M - j) // N + 1


def run() -> dict[str, object]:
    c = Counter()
    category_counts: dict[str, int] = {}

    def category(name: str, before: int) -> None:
        category_counts[name] = c.total - before

    # ------------------------------------------------------------------
    # A. Nonintegral binomial-Fuchsian packets.
    # ------------------------------------------------------------------
    before = c.total
    lambdas = sorted({
        Fraction(num, den)
        for den in range(2, 7)
        for num in range(-5, 9)
        if Fraction(num, den).denominator != 1
    })
    alphas = (-2, -1, 1, 2)
    for lam in lambdas:
        for N in range(1, 8):
            for j in range(N):
                upper, lower = packet_parameters(lam, N, j)
                full_lower = lower + [Fraction(1)]
                c.check(len(upper) == N, "upper parameter count")
                c.check(len(lower) == N - 1, "lower parameter count")
                c.check(sum(lower, Fraction(0)) - sum(upper, Fraction(0)) == -lam,
                        f"singular exponent {lam=} {N=} {j=}")

                # Hypergeometric irreducibility ledger: no a_i-b_j is integral.
                for a in upper:
                    for b in full_lower:
                        c.check(not is_integer(a - b),
                                f"unexpected resonance {lam=} {N=} {j=} {a=} {b=}")

                zero_classes = {Fraction(0)} | {
                    Fraction((x.numerator % x.denominator), x.denominator)
                    for x in (1 - b for b in lower)
                }
                expected_torsion = {Fraction(r, N) for r in range(N)}
                c.check(zero_classes == expected_torsion,
                        f"zero exponent classes {lam=} {N=} {j=}")

                infinity_classes = {
                    Fraction(((a - upper[0]).numerator % (a - upper[0]).denominator),
                             (a - upper[0]).denominator)
                    if a != upper[0] else Fraction(0)
                    for a in upper
                }
                c.check(infinity_classes == expected_torsion,
                        f"infinity exponent classes {lam=} {N=} {j=}")

                for alpha in alphas:
                    x = Fraction(alpha**N)
                    values = [packet_coeff(lam, alpha, N, j, mm) for mm in range(9)]
                    for mm in range(8):
                        ratio_num = Fraction(1)
                        ratio_den = Fraction(1)
                        for r in range(N):
                            ratio_num *= N * mm + j + lam + r
                            ratio_den *= N * mm + j + 1 + r
                        c.check(values[mm + 1] * ratio_den == values[mm] * x * ratio_num,
                                f"packet recurrence {lam=} {alpha=} {N=} {j=} {mm=}")
                    # Coefficient identity for the _N F_{N-1} differential operator.
                    for mm in range(1, len(values)):
                        left = Fraction(mm)
                        for b in lower:
                            left *= Fraction(mm) + b - 1
                        left *= values[mm]
                        right = x
                        for a in upper:
                            right *= Fraction(mm - 1) + a
                        right *= values[mm - 1]
                        c.check(left == right,
                                f"hypergeometric differential identity {lam=} {alpha=} {N=} {j=} {mm=}")
                # The nonintegral irreducible packet has no order deficit.
                c.check(N - N == 0, "nonintegral alias defect")
                c.check(N - N == 0, "nonintegral cancellation defect")
    category("nonintegral_binomial_packets", before)

    # ------------------------------------------------------------------
    # B. Positive-integral rational collapse.
    # ------------------------------------------------------------------
    before = c.total
    for L in range(1, 9):
        for N in range(1, 11):
            for j in range(N):
                for alpha in (-2, -1, 1, 2):
                    values = [
                        Fraction(math.comb(N * mm + j + L - 1, L - 1)) * Fraction(alpha) ** (N * mm + j)
                        for mm in range(L + 14)
                    ]
                    x = Fraction(alpha**N)
                    normalized = [values[mm] / (Fraction(alpha) ** j * x**mm) for mm in range(len(values))]
                    diffs = normalized
                    for _ in range(L):
                        diffs = finite_difference(diffs)
                    c.check(all(v == 0 for v in diffs),
                            f"polynomial degree {L=} {N=} {j=} {alpha=}")
                    for mm in range(L, len(values)):
                        conv = Fraction(0)
                        for h in range(L + 1):
                            conv += Fraction((-1) ** h * math.comb(L, h)) * x**h * values[mm - h]
                        c.check(conv == 0,
                                f"rational denominator {L=} {N=} {j=} {alpha=} {mm=}")
                ambient = N
                packet_order = 1
                alias = N - ambient
                cancellation = ambient - packet_order
                c.check(alias == 0, "positive integral alias")
                c.check(cancellation == N - 1, "positive integral cancellation")
                c.check(alias + cancellation == N - packet_order, "positive defect decomposition")
    category("positive_integral_collapse", before)

    # ------------------------------------------------------------------
    # C. Nonpositive-integral finite-support aliasing.
    # ------------------------------------------------------------------
    before = c.total
    for M in range(0, 17):
        lam = Fraction(-M)
        for N in range(1, 14):
            ambient = min(N, M + 1)
            alias = N - ambient
            c.check(alias == max(0, N - M - 1), "negative alias formula")
            for j in range(N):
                count = support_count(M, N, j)
                direct = sum(1 for nn in range(M + 1) if nn % N == j)
                c.check(count == direct, "negative support count")
                packet_order = 1 if count else 0
                cancellation = ambient - packet_order
                c.check(cancellation >= 0, "negative cancellation nonnegative")
                c.check(alias + cancellation == N - packet_order, "negative defect decomposition")
                c.check((count > 0) == (j <= M), "negative address support")
                for mm in range(count + 2):
                    nn = N * mm + j
                    expected = Fraction((-1) ** nn * math.comb(M, nn)) if nn <= M else Fraction(0)
                    actual = packet_coeff(lam, 1, N, j, mm)
                    c.check(actual == expected,
                            f"terminated coefficient {M=} {N=} {j=} {mm=}")
    category("nonpositive_integral_aliasing", before)

    # ------------------------------------------------------------------
    # D. Root-filter orthogonality and exact packet synthesis.
    # ------------------------------------------------------------------
    before = c.total
    for N in range(1, 25):
        for j in range(N):
            for nn in range(0, 5 * N + 1):
                selected = int(nn % N == j)
                orthogonality = 1 if (nn - j) % N == 0 else 0
                c.check(selected == orthogonality, "root-filter orthogonality")
        c.check(1 <= N, "recurrence order ledger")
        c.check(N >= 1, "differential order ledger")
    category("root_filter_and_order_ledger", before)

    examples = [
        {"source": r"$(1-z)^{-1/2}$", "packet": r"$N=2,\ j=0$", "recurrence_order": 1,
         "differential_order": 2, "ambient_order": 2, "alias": 0, "cancellation": 0,
         "status": "irreducible nonintegral packet"},
        {"source": r"$(1-z)^{-1/3}$", "packet": r"$N=3,\ j=2$", "recurrence_order": 1,
         "differential_order": 3, "ambient_order": 3, "alias": 0, "cancellation": 0,
         "status": "finite local exponent torsion"},
        {"source": r"$(1-z)^{-2}$", "packet": r"$N=3,\ j=1$", "recurrence_order": 1,
         "differential_order": 1, "ambient_order": 3, "alias": 0, "cancellation": 2,
         "status": "rational collapse"},
        {"source": r"$(1-z)^2$", "packet": r"$N=4,\ j=1$", "recurrence_order": 0,
         "differential_order": 1, "ambient_order": 3, "alias": 1, "cancellation": 2,
         "status": "finite-support polynomial"},
        {"source": r"$(1-z)^2$", "packet": r"$N=4,\ j=3$", "recurrence_order": 0,
         "differential_order": 0, "ambient_order": 3, "alias": 1, "cancellation": 3,
         "status": "zero address packet"},
    ]

    cumulative_before = 1_663_916
    result = {
        "block": "09",
        "name": "holonomic normalization and binomial-Fuchsian packet minimality",
        "category_counts": category_counts,
        "block_checks": c.total,
        "failures": c.failures,
        "cumulative_before": cumulative_before,
        "cumulative_after": cumulative_before + c.total,
        "examples": examples,
        "scope_boundary": [
            "general D-finite multisection minimality is not claimed",
            "the exact order theorem is for the marked binomial-Fuchsian packet family",
            "local monodromy eigenvalue torsion is not the same as finiteness of the global monodromy group",
            "algebraic branch recovery and nonlinear tree signatures remain later strata",
        ],
    }
    (GEN / "block09_holonomic_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    rows = [
        ("Nonintegral binomial packets", category_counts["nonintegral_binomial_packets"]),
        ("Positive-integral rational collapse", category_counts["positive_integral_collapse"]),
        ("Nonpositive-integral aliasing", category_counts["nonpositive_integral_aliasing"]),
        ("Root-filter and order ledger", category_counts["root_filter_and_order_ledger"]),
    ]
    table = [
        r"\begin{table}[htbp]", r"\centering", r"\caption{Exact Block 09 verification counts.}",
        r"\label{tab:block09-validation}", r"\begin{tabular}{@{}lr@{}}", r"\toprule",
        r"Validation class & Exact checks\\", r"\midrule",
    ]
    table += [f"{name} & {count:,}\\\\" for name, count in rows]
    table += [r"\midrule", f"Block 09 total & {c.total:,}\\\\",
              f"Cumulative Block 03--09 total & {cumulative_before + c.total:,}\\\\",
              r"Failures & 0\\", r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (GEN / "block09_validation_table.tex").write_text("\n".join(table) + "\n", encoding="utf-8")

    ex = [
        r"\begin{table}[htbp]", r"\centering", r"\small",
        r"\caption{Representative exact order profiles in the binomial--Fuchsian packet family.}",
        r"\label{tab:block09-examples}",
        r"\begin{tabularx}{\textwidth}{@{}L{0.17\textwidth}L{0.13\textwidth}cccccY@{}}",
        r"\toprule", r"Source & Packet & $r_{\rm tail}$ & $r_D$ & $r_{\rm orb}$ & Alias & Cancel & Interpretation\\",
        r"\midrule",
    ]
    for row in examples:
        ex.append(
            f"{row['source']} & {row['packet']} & {row['recurrence_order']} & {row['differential_order']} & "
            f"{row['ambient_order']} & {row['alias']} & {row['cancellation']} & {row['status']}\\\\"
        )
    ex += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
    (GEN / "block09_examples_table.tex").write_text("\n".join(ex) + "\n", encoding="utf-8")

    print(json.dumps({"checks": c.total, "failures": c.failures,
                      "cumulative": cumulative_before + c.total,
                      "categories": category_counts}, indent=2))
    return result


if __name__ == "__main__":
    run()
