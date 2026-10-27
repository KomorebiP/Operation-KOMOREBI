from __future__ import annotations

"""Exact finite audit for the Part IV semantic quotient extension.

This validates finite symbolic consequences and source contracts. It is not a
proof of the universal theorems and not independent peer review.
"""

from pathlib import Path
import json
import random
import re

import sympy as sp

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
GENERATED = ROOT / "generated"
RESULTS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)
OUT = RESULTS / "block17_semantic_extension_validation.json"
COUNTS = GENERATED / "block17_counts.tex"
TABLE = GENERATED / "block17_validation_table.tex"
SEED = 20260923
TRIALS = 1000


def random_matrix(rng: random.Random, rows: int, cols: int) -> sp.Matrix:
    return sp.Matrix([[rng.randint(-3, 3) for _ in range(cols)] for _ in range(rows)])


def span_rank(vectors: list[sp.Matrix]) -> int:
    return int(sp.Matrix.hstack(*vectors).rank()) if vectors else 0


def kernel_inclusion(a: sp.Matrix, b: sp.Matrix) -> bool:
    return all(b * v == sp.zeros(b.rows, 1) for v in a.nullspace())


def row_factor_exists(a: sp.Matrix, b: sp.Matrix) -> bool:
    return a.col_join(b).rank() == a.rank()


def main() -> None:
    rng = random.Random(SEED)
    failures: list[dict[str, object]] = []
    counts = {
        "semantic_exact_sequence": 0,
        "relative_residual": 0,
        "factorization_gate": 0,
        "quadratic_convex_identity": 0,
        "polyphase_hankel": 0,
        "source_contract": 0,
    }

    for trial in range(TRIALS):
        n = rng.randint(1, 10)
        A = random_matrix(rng, rng.randint(1, 10), n)
        B = random_matrix(rng, rng.randint(1, 10), n)
        nb = A.nullspace()
        mb = B.nullspace()
        dn, dm = len(nb), len(mb)
        dsum = span_rank(nb + mb)
        dint = dn + dm - dsum
        ds, dt = int(A.rank()), int(B.rank())
        dj, dc = n - dint, n - dsum

        counts["semantic_exact_sequence"] += 1
        if dj != ds + dt - dc:
            failures.append({"trial": trial, "kind": "semantic_exact_sequence"})

        counts["relative_residual"] += 1
        if dj != ds + (dn - dint):
            failures.append({"trial": trial, "kind": "relative_residual"})

        counts["factorization_gate"] += 1
        if kernel_inclusion(A, B) != row_factor_exists(A, B):
            failures.append({"trial": trial, "kind": "factorization_gate"})

    a, b, c = sp.symbols("a b c", real=True)
    d = a * b - c**2
    u = b * (a + b + 2*c) / d
    v = a * (a + b - 2*c) / d
    identity = sp.factor(a*b*((a+b)**2-4*c**2) - 4*d**2)
    target = sp.factor(a*b*(a-b)**2 + 4*c**2*d)
    counts["quadratic_convex_identity"] += 1
    if sp.expand(identity-target) != 0 or sp.factor(u*v-4) != sp.factor(target/d**2):
        failures.append({"kind": "quadratic_convex_identity"})

    z = sp.symbols("z", nonzero=True)
    for N in range(1, 9):
        S = sp.zeros(N)
        for j in range(N-1):
            S[j+1, j] = 1
        S[0, N-1] = z
        M = sp.eye(N) + S
        e0 = sp.zeros(N, 1)
        e0[0] = 1
        vals = [(e0.T * (M**n) * e0)[0] for n in range(2*N-1)]
        H = sp.Matrix(N, N, lambda i, j: vals[i+j])
        det = sp.factor(H.det())
        counts["polyphase_hankel"] += 1
        if sp.factor(det**2 - z**(2*(N-1))) != 0:
            failures.append({"kind": "polyphase_hankel", "N": N, "det": str(det)})

    required = {
        "block17_semantic_quotients.tex": [
            "thm:block17-universal-behavioral-coimage",
            "thm:block17-semantic-diamond",
            "thm:block17-task-change",
        ],
        "block18_carrier_observer_change.tex": [
            "thm:block18-carrier-factorization",
            "thm:block18-bridge-loss-exact",
            "thm:block18-observer-base-change",
            "thm:block18-polyphase-hankel-separation",
        ],
        "block19_admissibility_lifting.tex": [
            "thm:block19-admissibility-monotonicity",
            "thm:block19-convex-quadratic-separation",
            "thm:block19-relative-semantic-synthesis",
        ],
    }
    for filename, labels in required.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        for label in labels:
            counts["source_contract"] += 1
            if rf"\label{{{label}}}" not in text:
                failures.append({"kind": "source_contract", "file": filename, "label": label})
        counts["source_contract"] += 1
        if re.search(r"\b(?:TODO|TBD|PLACEHOLDER)\b", text):
            failures.append({"kind": "source_contract_literal", "file": filename})

    payload = {
        "schema": "komorebi.stratified-universality.block17-validation.v1",
        "seed": SEED,
        "arithmetic": "exact SymPy integer, rational, and polynomial algebra",
        "category_counts": counts,
        "assertions": sum(counts.values()),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
        "boundary": (
            "Finite exact computation and source-contract audit only. Universal statements "
            "are established by the written proofs; independent review is not claimed."
        ),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    COUNTS.write_text("\n".join([
        "% Generated by verify_block17_semantic_extension.py",
        rf"\newcommand{{\BlockSeventeenValidationAssertions}}{{{payload['assertions']:,}}}",
        rf"\newcommand{{\BlockSeventeenValidationFailures}}{{{len(failures):,}}}",
        rf"\newcommand{{\BlockSeventeenSemanticTrials}}{{{TRIALS:,}}}",
    ]) + "\n", encoding="utf-8")

    rows = [
        ("Semantic diamond dimension", counts["semantic_exact_sequence"]),
        ("Relative residual dimension", counts["relative_residual"]),
        ("Carrier factorization gate", counts["factorization_gate"]),
        ("Quadratic/convex symbolic identity", counts["quadratic_convex_identity"]),
        ("Polyphase Hankel determinants", counts["polyphase_hankel"]),
        ("Theorem-source contracts", counts["source_contract"]),
    ]
    lines = [
        r"\begin{table}[htbp]", r"\centering", r"\small",
        r"\caption{Exact finite and symbolic audit for the Part IV semantic quotient extension.}",
        r"\label{tab:block17-validation}",
        r"\begin{tabular}{@{}lr@{}}", r"\toprule",
        r"Audit family & Assertions\\", r"\midrule",
    ]
    lines += [f"{name} & {count:,}\\\\" for name, count in rows]
    lines += [r"\midrule", rf"\textbf{{Total}} & \textbf{{{payload['assertions']:,}}}\\",
              rf"Recorded failures & {len(failures):,}\\", r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TABLE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": payload["status"], "assertions": payload["assertions"], "failures": len(failures)}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
