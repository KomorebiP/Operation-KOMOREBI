from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import csv
import json

import sympy as sp

from special_functions import (
    block_appell_polynomials,
    congruential_euler_coefficients,
    registry_entries,
    secant_coefficients,
    secant_parameter_polynomial,
    theta_polynomials,
    transfer_tangent_coefficients,
    write_registry,
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (RESULTS / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


write_registry(RESULTS)

secant_rows: list[dict[str, object]] = []
for N in range(2, 11):
    for order in range(1, 5):
        coeff = secant_coefficients(N, order, 10)
        for n, value in enumerate(coeff):
            secant_rows.append({"N": N, "order": order, "n": n, "coefficient": fraction_text(value)})
write_csv("transfer_secant_coefficients.csv", ["N", "order", "n", "coefficient"], secant_rows)

tangent_rows: list[dict[str, object]] = []
for N in range(2, 11):
    coeff = transfer_tangent_coefficients(N, 10)
    for n, value in enumerate(coeff):
        tangent_rows.append({"N": N, "n": n, "degree": N * n + N - 1, "coefficient": fraction_text(value)})
write_csv("transfer_tangent_coefficients.csv", ["N", "n", "degree", "coefficient"], tangent_rows)

ce_rows: list[dict[str, object]] = []
for N in range(2, 11):
    for j in range(N):
        coeff = congruential_euler_coefficients(N, j, 8)
        for n, value in enumerate(coeff):
            ce_rows.append({"N": N, "j": j, "n": n, "degree": N * n, "coefficient": fraction_text(value)})
write_csv("congruential_euler_coefficients.csv", ["N", "j", "n", "degree", "coefficient"], ce_rows)

parameter_rows: list[dict[str, object]] = []
for N in range(2, 9):
    for n in range(0, 8):
        parameter_rows.append({"N": N, "n": n, "polynomial": str(secant_parameter_polynomial(N, n))})
write_csv("secancy_parameter_polynomials.csv", ["N", "n", "polynomial"], parameter_rows)

theta_rows = [{"m": m, "degree": 2 * m, "polynomial": str(poly)} for m, poly in enumerate(theta_polynomials(8))]
write_csv("theta_polynomials.csv", ["m", "degree", "polynomial"], theta_rows)

appell_rows: list[dict[str, object]] = []
for N, j, order in [(3, 1, 1), (4, 1, 1), (5, 2, 1), (5, 2, 2)]:
    polys = block_appell_polynomials(N, j, order, 12)
    for m, poly in enumerate(polys):
        appell_rows.append({"N": N, "j": j, "order": order, "m": m, "polynomial": str(sp.factor(poly))})
write_csv("block_appell_polynomials.csv", ["N", "j", "order", "m", "polynomial"], appell_rows)

summary = {
    "author": "Komorebi P.",
    "canonical_registry_entries": len(registry_entries()),
    "generated_rows": {
        "transfer_secants": len(secant_rows),
        "transfer_tangents": len(tangent_rows),
        "congruential_euler": len(ce_rows),
        "secancy_parameter_polynomials": len(parameter_rows),
        "theta_polynomials": len(theta_rows),
        "block_appell_polynomials": len(appell_rows),
    },
    "scope_note": (
        "The tables enumerate canonical families and representative parameter ranges. "
        "The unrestricted construction F -> B_{N,j}F generates an infinite class and is documented as a schema."
    ),
}
(RESULTS / "catalog_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
