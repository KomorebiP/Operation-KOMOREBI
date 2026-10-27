from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated_tables"
OUT.mkdir(exist_ok=True)

results = json.loads((ROOT / "results" / "results.json").read_text())

checks = list(csv.DictReader((ROOT / "results" / "checks.csv").open()))
with (OUT / "checks_summary.tex").open("w") as handle:
    handle.write("\\begin{longtable}{p{0.78\\textwidth}p{0.12\\textwidth}}\n")
    handle.write(
        "\\caption{Built-in computational certificates. Full numerical details are retained in the JSON ledger.}"
        "\\label{tab:checks}\\\\\n"
    )
    handle.write("\\toprule Check & Result \\\\ \\midrule\n\\endfirsthead\n")
    handle.write("\\toprule Check & Result \\\\ \\midrule\n\\endhead\n")
    for row in checks:
        name = row["name"].replace("_", "\\_")
        result = "pass" if row["passed"] == "True" else "fail"
        handle.write(f"{name} & {result} " + r"\\" + "\n")
    handle.write("\\bottomrule\n\\end{longtable}\n")

rows = list(csv.DictReader((ROOT / "tables" / "gamma_dephasing.csv").open()))
with (OUT / "gamma_dephasing.tex").open("w") as handle:
    handle.write("\\begin{table}[H]\n\\centering\n")
    handle.write("\\caption{Selected values of the limiting Gamma dephasing function for $a=\\beta=2$.}\n")
    handle.write("\\begin{tabular}{rrrr}\n\\toprule $\\tau$ & Real part & Imaginary part & Squared modulus \\\\ \\midrule\n")
    for row in rows:
        handle.write(
            f"{float(row['tau']):.0f} & {float(row['real']):.8f} & "
            f"{float(row['imag']):.8f} & {float(row['modulus_squared']):.8f} "
            + r"\\" + "\n"
        )
    handle.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

rows = list(csv.DictReader((ROOT / "tables" / "pade_nodes.csv").open()))
with (OUT / "pade_nodes.tex").open("w") as handle:
    handle.write("\\begin{table}[H]\n\\centering\n")
    handle.write("\\caption{Four-packet Pad\\'e nodes and weights for the positive companion and signed M\\\"obius sequences.}\n")
    handle.write("\\small\n\\begin{tabular}{lrrrr}\n\\toprule Family & Node real & Node imag. & Weight real & Weight imag. \\\\ \\midrule\n")
    for row in rows:
        handle.write(
            f"{row['family']} & {float(row['node_real']):.9f} & {float(row['node_imag']):.2e} & "
            f"{float(row['weight_real']):.9f} & {float(row['weight_imag']):.2e} "
            + r"\\" + "\n"
        )
    handle.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

with (OUT / "headline.tex").open("w") as handle:
    handle.write(
        "\\[\\boxed{" + str(results["passed"]) + "/" + str(results["checks"])
        + "\\text{ built-in checks passed}}\\]\n"
    )
