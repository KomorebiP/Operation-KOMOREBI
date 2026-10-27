from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "tables"
OUT = ROOT / "generated_tables"
OUT.mkdir(exist_ok=True)


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scientific(value: str | float, digits: int = 4) -> str:
    number = float(value)
    if number == 0:
        return "0"
    return f"{number:.{digits}e}"


rows = read_csv("stieltjes_derivatives.csv")
lines = [
    r"\begin{tabular}{rrrr}",
    r"\toprule",
    r"$n$ & packet formula & direct derivative & absolute error\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['order']} & {float(row['predicted']):.12f} & {float(row['numeric']):.12f} & {scientific(row['error'], 2)}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "stieltjes_derivatives.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("character_derivatives.csv")
lines = [
    r"\begin{tabular}{rrrr}",
    r"\toprule",
    r"$m$ & Stieltjes packet sum & $L$-derivative formula & error\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['order']} & {float(row['packet_sum_real']):.10f} & {float(row['formula_real']):.10f} & {scientific(row['error'], 2)}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "character_derivatives.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("energy_asymptotic.csv")
lines = [
    r"\begin{tabular}{rrrr}",
    r"\toprule",
    r"$k$ & $E_k$ & $k^{3/2}E_k$ & relative error\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['k']} & {scientific(row['energy'], 6)} & {float(row['scaled']):.10f} & {scientific(row['relative_error'], 3)}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "energy_asymptotic.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("gamma_scaling.csv")
lines = [
    r"\begin{tabular}{rrrrrrr}",
    r"\toprule",
    r"$k$ & mean & variance & $q_{0.1}$ & $q_{0.5}$ & $q_{0.9}$ & KS\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['k']} & {float(row['mean']):.5f} & {float(row['variance']):.5f} & {float(row['q10']):.5f} & {float(row['q50']):.5f} & {float(row['q90']):.5f} & {float(row['ks']):.5f}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "gamma_scaling.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("character_decoherence.csv")
lines = [
    r"\begin{tabular}{rr}",
    r"\toprule",
    r"$k$ & largest normalized off-diagonal entry\\",
    r"\midrule",
]
for row in rows:
    lines.append(f"{row['k']} & {float(row['max_offdiag']):.8f}\\\\")
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "character_decoherence.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("hankel.csv")
lines = [
    r"\begin{tabular}{rrr}",
    r"\toprule",
    r"size & smallest eigenvalue & largest eigenvalue\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['size']} & {scientific(row['minimum_eigenvalue'], 3)} & {scientific(row['maximum_eigenvalue'], 3)}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "hankel.tex").write_text("\n".join(lines), encoding="utf-8")

rows = read_csv("zeta_ratio.csv")
lines = [
    r"\begin{tabular}{rrrr}",
    r"\toprule",
    r"$k$ & direct energy & zeta-ratio difference & truncation error\\",
    r"\midrule",
]
for row in rows:
    lines.append(
        f"{row['k']} & {scientific(row['direct'], 7)} & {scientific(row['zeta_ratio'], 7)} & {scientific(row['truncation_error'], 3)}\\\\"
    )
lines.extend([r"\bottomrule", r"\end{tabular}"])
(OUT / "zeta_ratio.tex").write_text("\n".join(lines), encoding="utf-8")

summary = json.loads((ROOT / "results" / "results.json").read_text())
(OUT / "checks_summary.tex").write_text(
    "\\boxed{" + str(summary["passed"]) + "/" + str(summary["checks"]) + "\\text{ checks passed}}",
    encoding="utf-8",
)
