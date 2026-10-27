"""Pin the current mathematical figure sources and bounded data checks.

This helper refreshes hashes only after its named review has been performed.
It is not an automated replacement for reviewing a changed figure formula.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("historical_audit", ROOT / "historical/catalan_packet_audit.py")
packet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packet)
data = json.loads((ROOT / "evidence/computation/independent_final/diagnostic_data.json").read_text())
u, v = packet.zudilin_sequences(60)
checks = {
    "F_1_1_exact_coefficients": {
        "G_coefficient": str(-8 * (16 * u[1] + 256 * u[2])),
        "constant": str(8 * (16 * v[1] + 256 * v[2])),
    },
    "bounded_v2_grid_pair_count": sum(len(row["v2"]) for row in data["binomial_v2_grid"]),
    "bounded_v2_grid_minimum": min(x for row in data["binomial_v2_grid"] for x in row["v2"]),
    "bounded_v2_grid_maximum": max(x for row in data["binomial_v2_grid"] for x in row["v2"]),
    "prefix_maxima_match_grid": all(row["maximum_v2"] == max(x for g in data["binomial_v2_grid"] if g["n"] <= row["n_max"] for x in g["v2"]) for row in data["binomial_v2_prefix_maxima"]),
    "sign_grid_count": len(data["raw_filter_grid"]),
    "all_even_m_signs_positive": all(row["certified_sign"] > 0 for row in data["raw_filter_grid"] if row["m"] % 2 == 0),
    "five_minimal_gcds": [row["minimal_pair_gcd"] for row in data["cleared_gcd_decomposition"]],
    "five_gcd_decompositions_match": all(int(row["redundant_scale_Q_over_D"]) * int(row["minimal_pair_gcd"]) == int(row["cleared_gcd"]) for row in data["cleared_gcd_decomposition"]),
}
FIGURES = [
    ("01_constant", "Defining series and decimal marker only", "mpmath at 120 digits is display, not rationality evidence"),
    ("02_alternating_series", "Exact N-term sums and error bound (2N+1)^-2", "Fraction sums N = 1 to 14, universal alternating theorem separate"),
    ("03_log_integral", "G=integral -log(x)/(1+x^2) dx", "1100 floating coordinates, height clipped at 5.5, no quadrature claim"),
    ("04_double_integral", "G=double integral 1/(1+x^2*y^2)", "160 by 160 floating contour, termwise identity via absolute summability of integrated terms"),
    ("05_beta_family", "beta(1) = pi/4, beta(2) = G, beta(3) = pi^3/32", "Known odd-value identities, no implication deciding beta(2)"),
    ("06_rationality_lattice", "b(AG-B)=aA-bB integer under G=a/b", "Conditional lattice contradiction, b>0 and integer A,B"),
    ("07_series_denominators", "Reduced denominators and alternating upper error bound", "Exact Fraction denominators N<=60; plotted bound is not exact error"),
    ("08_error_clearing", "D_N G-P_N=D_N(G-s_N)", "Exact scaling identity"),
    ("09_recurrence_structure", "A_n*x_(n+1)=q(n)*x_n+C_n*x_(n-1)", "Historical formula n>=1; guide calls q(n) as Q_n consistently"),
    ("10_initial_sequences", "Exact u,v,v/u for n = 0 to 3", "Fraction recurrence"),
    ("11_recurrence_growth", "Leading characteristic polynomial lambda^2-11lambda-1", "Exact u_n<=60 converted to logs; curve does not prove asymptotic"),
    ("12_approximant_error", "Log|G-v/u| lower bracket display", "Exact rational interval evidence at n = 0, 1, 2, 5, 10, 20, 40; rounded logarithms"),
    ("13_wronskian", "Alternating nonzero W_n formula", "Exact determinant n<=40; universal written induction separate"),
    ("14_wronskian_identity", "W_n=-(C_n/A_n)W_(n-1),W0 = -13/8", "Universal algebra, no limiting input"),
    ("15_scaled_coefficients", "T_n=16^n u_n", "Initial integers at n = 0 to 5; exact recurrence divisions through n = 10000 separate from universal proof"),
    ("16_pascal_transform", "S_(n,m+1)=S_(n,m)+S_(n+1,m)", "Universal binomial coefficient addition"),
    ("17_binomial_packet", "S_(1,4) weights 1, 4, 6, 4, 1", "Exact positive terms T1 to T5, logs display; no divisibility inference from size"),
    ("18_modular_exactness", "Nonzero residue gives exact v2 below K", "K = 128 finite run has no zero residues; zero would give only lower bound"),
    ("19_v2_heatmap", "v2(S_(n,m)) direct grid", "20,300 pairs, n <= 100, m <= 4n; min 2 and max 20 cover all cells"),
    ("20_prefix_maxima", "Maximum v2 on finite triangular prefixes", "Independent N <= 100, max 20; default N = 2000, max 31; no universal bound"),
    ("21_scan_domain", "Domain n = 1 to 2000, m = 0 to 4n", "8,006,000 pairs; first loop-order maximum 31 at (1466, 2113); not uniqueness"),
    ("22_lcm_growth", "Exact L_t with log display and reference line t", "LCM t<=300, graph alone does not prove PNT asymptotic"),
    ("23_gcd_rate", "log cleared gcd/(n+m)", "Five exact rows, rounded logs; no asymptotic inference"),
    ("24_gcd_decomposition", "d_cleared=(Q/D)*g_minimal", "Exact five rows, minimal gcds 8, 4, 8, 64, 8; logs display"),
    ("25_threshold_plane", "Exponent c-delta-h under explicit assumed exponential equalities", "Schematic delta = 1.5; actual available upper bound is not equality; equality boundary unresolved"),
    ("26_finite_countermodels", "Two synthetic sequences share prefix through index 50", "Synthetic, not fitted Catalan predictions; divergent/vanishing tails illustrate nonimplication"),
    ("27_filter_signs", "Signed F=8(-1)^n sum binom(m,i)16^(n+i)(uG-v)=16^n Jtilde", "860 exact rational sign cells; even positivity consistent; odd alternating rule false"),
    ("28_conditional_route", "Integer plus nonzero plus vanishing implies irrational", "Exact conditional theorem, not unconditional application"),
    ("29_evidence_boundaries", "Identities, external inputs, finite checks, unresolved decay", "No irrationality proof or proof-assistant certificate"),
    ("30_integral_filter", "Jtilde=integral psi^n(1-16psi)^m dmu", "Illustrative polynomial powers 1 and 2 on correct range 0 to phi^-5; even nonnegativity, positive interior set, no quadrature claim"),
    ("31_source_rate", "M=max of two branches; eta=(logR+alpha log(1+R)-log16-logM)/(4(1+alpha)+logR+alpha log(1+R))", "Numeric alpha = 0 to 5 formula evaluations; source maximum 0.62335 attributed, M remains an upper bound for actual integral"),
]
provenance = json.loads((ROOT / "visual/figure_provenance.json").read_text())
by_name = {x["figure"]: x for x in provenance["figures"]}
records = []
for name, formula, scope in FIGURES:
    file = ROOT / "visual/figures" / f"{name}.pdf"
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    png_digest = hashlib.sha256(file.with_suffix(".png").read_bytes()).hexdigest()
    records.append({"figure": f"{name}.pdf", "formula_review": formula, "data_and_scope_review": scope,
                    "status": "passed", "pdf_sha256": digest,
                    "png_sha256": png_digest,
                    "provenance_hash_matches": by_name[f"{name}.pdf"]["sha256"] == digest,
                    "provenance_png_hash_matches": by_name[f"{name}.pdf"]["png_sha256"] == png_digest})
inputs = ["visual/figures.py", "visual/main.tex", "visual/figure_provenance.json",
          "evidence/computation/independent_final/diagnostic_data.json",
          "evidence/computation/historical_default/results.json", "historical/catalan_packet_audit.py",
          "literature/source_contracts.md"]
result = {"schema_version": 1, "project": "Catalan Series 08", "reviewer": "catalan_audit_finish", "date": "2026-10-09",
          "status": "passed for pinned sources; changed formulas require renewed review", "coverage": "all 31 figure formulas and data inspected; layout handled separately",
          "source_inputs": [{"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in inputs],
          "checks": checks, "figures": records, "mathematical_changes": [],
          "limits": ["No large scan rerun by this reviewer", "External result hypotheses use separately authenticated literature contracts",
                     "Rounded coordinates/logarithms are display aids", "This is not a figure layout certificate"],
          "diagnostic_failures": [{"cause": "Initial checkpoint assumed row key gcd instead of actual cleared_gcd", "effect": "KeyError before report write; corrected after schema inspection"}]}
assert all(row["provenance_hash_matches"] for row in records)
assert all(row["provenance_png_hash_matches"] for row in records)
assert checks["prefix_maxima_match_grid"] and checks["five_gcd_decompositions_match"]
assert checks["all_even_m_signs_positive"] and checks["bounded_v2_grid_pair_count"] == 20300
(ROOT / "audits/figure_data_review.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(checks, indent=2))
