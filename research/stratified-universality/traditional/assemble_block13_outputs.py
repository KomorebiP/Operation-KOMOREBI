from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(parents=True, exist_ok=True)

bridge_path = GEN / "block13_bridge_synthesis_validation.json"
invariant_path = GEN / "block13_global_invariant_validation.json"
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
invariant = json.loads(invariant_path.read_text(encoding="utf-8"))

for name, record in (("bridge", bridge), ("invariant", invariant)):
    if not record.get("passed"):
        raise RuntimeError(f"Block 13 {name} verifier did not pass")
    failures = record.get("failures", [])
    if failures not in ([], 0, None):
        raise RuntimeError(f"Block 13 {name} verifier recorded failures: {failures}")

prior = int(bridge["prior_cumulative"])
bridge_checks = int(bridge["checks"])
invariant_checks = int(invariant["checks"])
replayed_checks = int(bridge.get("categories", {}).get("record_authentication", 0)) + int(bridge.get("categories", {}).get("periodic_component_replay", 0))
executed_checks = bridge_checks + invariant_checks
new_block_checks = executed_checks - replayed_checks
cumulative_unique = prior + new_block_checks
cumulative_executed = prior + executed_checks

summary = {
    "artifact": "Block 13 combined invariant-descent validation summary",
    "passed": True,
    "prior_cumulative": prior,
    "bridge_synthesis_checks": bridge_checks,
    "weighted_qary_and_federated_checks": invariant_checks,
    "regression_and_authentication_checks": replayed_checks,
    "block13_new_checks": new_block_checks,
    "block13_executed_checks": executed_checks,
    "cumulative_unique_block_checks": cumulative_unique,
    "cumulative_executed_assertions": cumulative_executed,
    "failures": 0,
    "boundary": (
        "The total is the number of exact assertions executed by two complementary suites. "
        "It is not a count of independent theorems. The first suite audits the bridge matrix, "
        "periodic and product-multiplicative overlap replays, directional losses, Cech holonomy, "
        "and completeness gates. The second audits the weighted q-ary tree-algebraic-holonomic "
        "overlap, packet equations, and tagged component separation."
    ),
}
(GEN / "block13_combined_validation.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

counts = "\n".join(
    [
        rf"\newcommand{{\BlockThirteenBridgeChecks}}{{{bridge_checks:,}}}",
        rf"\newcommand{{\BlockThirteenInvariantChecks}}{{{invariant_checks:,}}}",
        rf"\newcommand{{\BlockThirteenRegressionChecks}}{{{replayed_checks:,}}}",
        rf"\newcommand{{\BlockThirteenNewChecks}}{{{new_block_checks:,}}}",
        rf"\newcommand{{\BlockThirteenChecks}}{{{executed_checks:,}}}",
        rf"\newcommand{{\BlockThirteenCumulative}}{{{cumulative_unique:,}}}",
        rf"\newcommand{{\BlockThirteenCumulativeExecuted}}{{{cumulative_executed:,}}}",
    ]
) + "\n"
(GEN / "block13_counts.tex").write_text(counts, encoding="utf-8")

validation_table = rf"""\begin{{table}}[htbp]
\centering
\caption{{Exact verification of the Block 13 global-invariant and cross-stratum synthesis layer.}}
\label{{tab:block13-combined-validation}}
\small
\begin{{tabularx}}{{\textwidth}}{{@{{}}Y r@{{}}}}
\toprule
Validation suite & Exact assertions\\
\midrule
Bridge matrix, overlap replay, directional-loss, and finite \v{{C}}ech suite & {bridge_checks:,}\\
Weighted $q$-ary tree--algebraic--holonomic and tagged-invariant suite & {invariant_checks:,}\\
\midrule
Regression/authentication assertions already represented in Blocks 03--12 & {replayed_checks:,}\\
\textbf{{New Block 13 comparison and coherence assertions}} & \textbf{{{new_block_checks:,}}}\\
All assertions executed by the two Block 13 suites & {executed_checks:,}\\
Failures & 0\\
\bottomrule
\end{{tabularx}}
\end{{table}}
"""
(GEN / "block13_combined_validation_table.tex").write_text(validation_table, encoding="utf-8")

bridge_matrix = r"""\begin{landscape}
\begin{table}[p]
\centering
\caption{Authoritative broad-stratum bridge matrix after Block 13. Every decorated equivalence is restricted to the named normalized overlap; the undecorated broad categories are not thereby identified.}
\label{tab:block13-bridge-matrix}
\scriptsize
\setlength{\tabcolsep}{3.7pt}
\begin{tabular}{@{}lcccccccc@{}}
\toprule
Source $\backslash$ target & LIN & HOL & DIG & ALG & TREE & PROD & LOC & GAL\\
\midrule
LIN  & $\mathsf E$ & $\mathsf{FF}$ & $\mathsf E_{\rm per}$ & -- & -- & -- & $\mathsf E_{\rm per}$ & --\\
HOL  & $\mathsf P$ & $\mathsf E$ & -- & $\mathsf E_{\rm Fuss}/\mathsf P$ & $\mathsf E_{\rm Fuss}/\mathsf P$ & -- & -- & --\\
DIG  & $\mathsf E_{\rm per}$ & $\mathsf P$ & $\mathsf E$ & $\mathsf P$ & -- & -- & $\mathsf E_{\rm rm}$ & --\\
ALG  & -- & $\mathsf E_{\rm Fuss}/\mathsf D$ & $\mathsf P$ & $\mathsf E$ & $\mathsf E_{\rm Fuss}/\mathsf P$ & -- & -- & --\\
TREE & -- & $\mathsf E_{\rm Fuss}/\mathsf D$ & -- & $\mathsf E_{\rm Fuss}/\mathsf D$ & $\mathsf E$ & -- & -- & --\\
PROD & $\mathsf D$ & -- & -- & -- & -- & $\mathsf E$ & $\mathsf P$ & --\\
LOC  & $\mathsf E_{\rm per}$ & -- & $\mathsf E_{\rm rm}$ & -- & -- & $\mathsf P$ & $\mathsf E$ & --\\
GAL  & -- & -- & -- & -- & -- & -- & -- & $\mathsf E$\\
\bottomrule
\end{tabular}
\vspace{5pt}
\parbox{0.96\linewidth}{\scriptsize
\textbf{Legend.} $\mathsf E$: equivalence; $\mathsf{FF}$: fully faithful inclusion; $\mathsf D$: information-losing directional functor; $\mathsf P$: partial, constructor-dependent, or certificate-dependent bridge; --: no certified bridge. The subscripts $\mathrm{per}$, $\mathrm{rm}$, and $\mathrm{Fuss}$ denote the unit-periodic, rational functional-Mahler, and marked weighted Fuss overlaps. A cell of the form $\mathsf E_{\mathrm{Fuss}}/\mathsf D$ means equivalence on the marked Fuss slice and directional loss on the ambient bridge. Functional-Mahler coefficient equations and Newton--Mahler interpolation remain distinct despite sharing the LOC row.}
\end{table}
\end{landscape}
"""
(GEN / "block13_bridge_matrix.tex").write_text(bridge_matrix, encoding="utf-8")

component_table = r"""\begin{table}[htbp]
\centering
\caption{Certified connected components of the Block 13 atlas.}
\label{tab:block13-components}
\tiny
\begin{tabularx}{\textwidth}{@{}L{0.105\textwidth}L{0.255\textwidth}L{0.285\textwidth}Y@{}}
\toprule
Component & Semantic domain and normalized charts & Complete coordinate and reversible overlap & Directional satellites or exact boundary\\
\midrule
DRLM & fixed-prime regular sequences; canonical section module, strict shortlex record, and minimal DFAO; rational-mask/Cartier and periodic linear subcharts & strict shortlex pointed digit-linear record, refined on the rational-mask and unit-periodic full replete subcategories & integral reductions and Newton--Mahler interpolation are directional; many automatic sequences have no rational mask\\
LOC & continuous $\mathbb Z_p$-valued functions; Newton--Mahler coefficients, complete clopen branch packets, and affine branch coordinates & canonical Mahler coefficient sequence; complete branch analysis and synthesis at each declared depth & functional-Mahler equations require a separately declared coefficient lift and interpolation constructor\\
Fuss & marked $U=z+\alpha U^q$ tree system, selected algebraic branch, and compressed P-recursive coefficient chart & parameter pair $(q,\alpha)$ with its support and singularity-orbit package & forgetting the branch mark or generator grammar is information-losing\\
EM & fixed-basis Euler exponents, divisor ghosts, integral unit series, and prime-uniform multiplicative local factors & Euler exponent sequence on the fixed-basis, prime-uniform essential image & arbitrary product grammars and nonuniform prime-local fields remain outside the reversible overlap\\
Gal & subgroup, fixed field, and faithful Reynolds projector for one fixed finite Galois extension & actual subgroup $H\leq G$ with functorial core, normal-closure, and double-coset data & projective Brauer obstruction, modular or wild failure, and the tensor-fiber gate remain separately typed\\
\bottomrule
\end{tabularx}
\end{table}
"""
(GEN / "block13_component_table.tex").write_text(component_table, encoding="utf-8")

print(json.dumps(summary, sort_keys=True))
