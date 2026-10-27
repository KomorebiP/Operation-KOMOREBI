#!/usr/bin/env python3
"""Generate the Paper IV record register from the canonical TeX source."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "paper4.tex"
OUTPUT = ROOT / "provenance" / "THEOREM_REGISTER.md"

ENVIRONMENTS = (
    "theorem",
    "proposition",
    "lemma",
    "corollary",
    "definition",
    "example",
    "remark",
    "standardfact",
    "boundary",
)
RESULTS = {"theorem", "proposition", "lemma", "corollary"}
FULL_LEAN = {
    "cor:complete_symmetric_form",
    "cor:leading_dominant_zero",
    "cor:orbit_reduced_asymptotic",
    "cor:secant_asymptotic",
    "prop:normalized_section_product",
    "thm:nearest_circle_expansion",
    "thm:trace_class_model",

    "thm:indicator_polygon",
    "thm:newton_sums",
    "cor:mittag_leffler_tangent",
    "prop:theta_bell",
    "cor:tangent_zero_sums",
    "cor:reciprocal_zero_data",
    "thm:zeta_continuation",
    "cor:exact_zeta_models",
    "cor:branch_grouped_continuation",
    "cor:N3_zero_correction",
    "thm:derivative_weighted_convergence",
    "thm:zeta_convergence",
    "cor:eventual_simplicity",
    "cor:reduced_zeros",
    "thm:zero_counting",
    "cor:exponent_of_convergence",
    "thm:genus_zero_product",

    "lem:two_term_dominance",
    "thm:large_zero_strings",
    "thm:first_zero_correction",
    "prop:orders",
    "lem:near_cancellation",
    "cor:case_two_zeros",
    "cor:wronskians",
    "cor:signed_wronskian",
    "thm:reciprocal_bell",
    "thm:root_filter",
    "prop:covariance",
    "thm:cyclic_product",
    "thm:exponential_cycle",
    "cor:exponential_addition",
    "thm:hypergeometric_form",
    "prop:signed_exponential_relation",
    "thm:signed_cycle",
    "prop:signed_addition",
    "thm:finite_exponential_representation",
    "cor:denominator_symmetries",
    "thm:finite_algebra_exponentials",
    "thm:companion_matrix_realization",
    "cor:fundamental_matrix_entries",
    "cor:companion_addition_inversion",
    "thm:parameter_recurrence",
    "thm:reciprocal_parameter_addition",
    "cor:binomial_type",
    "thm:logarithmic_newton_recurrence",
    "cor:first_reciprocal_polynomials",
    "cor:factor_r",
    "prop:tangent_kappa",
    "thm:tangent_recurrence",
    "cor:reciprocal_derivative",
    "thm:higher_riccati",
    "thm:triangular_inverse",
    "thm:residue_section_parameter_addition",
    "thm:appell_laws",
    "prop:explicit_appell",
    "thm:appell_two_parameter_convolution",
    "prop:appell_operator_form",
    "cor:appell_symmetry",
    "thm:theta_reconstruction",
    "prop:theta_factors",
    "prop:theta_newton_recurrence",
}
CONDITIONAL = {
    "thm:nearest_circle_expansion",
    "cor:leading_dominant_zero",
    "cor:orbit_reduced_asymptotic",
}


def cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    section = 0
    counter = 0
    records: list[tuple[str, str, str, str, str]] = []

    token = re.compile(
        r"\\section\*?\{(?P<section>[^{}]*)\}"
        r"|\\begin\{(?P<env>" + "|".join(ENVIRONMENTS) + r")\}"
        r"(?:\[(?P<title>[^\]]*)\])?"
    )
    positions = list(token.finditer(source))
    for index, match in enumerate(positions):
        section_title = match.group("section")
        if section_title is not None:
            if not match.group(0).startswith(r"\section*"):
                section += 1
                counter = 0
            continue

        env = match.group("env")
        if env is None:
            continue
        counter += 1
        end = positions[index + 1].start() if index + 1 < len(positions) else len(source)
        block = source[match.end() : end]
        label_match = re.search(r"\\label\{([^{}]+)\}", block)
        label = label_match.group(1) if label_match else ""
        title = match.group("title") or "(untitled)"

        if env in RESULTS:
            evidence = "P + L(full)" if label in FULL_LEAN else "P"
            status = "Conditional article theorem" if label in CONDITIONAL else "Article theorem"
        elif env == "standardfact":
            evidence = "I"
            status = "Imported standard fact"
        elif env in {"definition"}:
            evidence = "D"
            status = "Definition"
        elif env in {"example"}:
            evidence = "E"
            status = "Example"
        else:
            evidence = "R"
            status = "Remark or boundary"

        records.append((f"{section}.{counter}", env.title(), title, label, f"{evidence}; {status}"))

    result_count = sum(1 for _, env, _, _, _ in records if env.lower() in RESULTS)
    proof_count = len(re.findall(r"\\begin\{proof\}", source))
    standard_count = sum(1 for _, env, _, _, _ in records if env == "Standardfact")

    lines = [
        "# Paper IV mathematical record register",
        "",
        "Generated from `paper/paper4.tex` by `scripts/generate_register.py`.",
        "",
        f"- Numbered records: `{len(records)}`",
        f"- Theorem-like results: `{result_count}`",
        f"- Proof environments: `{proof_count}`",
        f"- Imported standard facts: `{standard_count}`",
        "",
        "Evidence codes: `P` = article proof, `L(full)` = the full scoped",
        "manuscript statement is mapped to Lean, `I` = imported fact, `D` = definition,",
        "`E` = example, and `R` = remark or boundary. The Lean theorem map, rather",
        "than this summary code, is authoritative for the exact formal statement.",
        "",
        "| No. | Type | Title | Label | Evidence and status |",
        "|---:|---|---|---|---|",
    ]
    for number, env, title, label, status in records:
        lines.append(
            f"| {number} | {cell(env)} | {cell(title)} | `{cell(label)}` | {cell(status)} |"
        )
    lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
