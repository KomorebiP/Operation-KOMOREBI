#!/usr/bin/env python3
"""Prepare current release documents while preserving the prior mathematical checklist."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1] / "output/PRSC_IX_Complete_Parameter_Charts.zip"
with zipfile.ZipFile(BASE) as archive:
    checklist = archive.read("PRSC_IX_Complete_Parameter_Charts/REMAINING_CHECKLIST.md").decode()

def replace_once(old, new):
    global checklist
    assert checklist.count(old) == 1, old[:80]
    checklist = checklist.replace(old, new)

replace_once("**Current chart block: fresh verification PASS.**", "**Current weighted lifting block: fresh verification PASS.**")
weighted = r"""- [x] **Weighted nonlinear lifting — current block.** For prime \(p\), let \(R=\mathbb Z_p\), \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(J=DF(a)\). If
  \[
  J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad
  F(a)\in p^rR^d,\qquad r>2s,
  \]
  then
  \[
  \exists!\,b\in a+p^{s+1}R^d:\ F(b)=0,
  \qquad b-a\in p^{r-s}R^d.
  \]
  Uniqueness holds throughout the full stated ball. The same exponent \(s\) is retained. This includes arbitrary p-adic coefficients and centers, every prime, and finite square dimension. The integral certificate \(AJ=JA=p^sI\) is proved equivalent to the fraction-field inverse condition. The strict threshold and absence of a universally available extra precision digit have explicit Lean controls.

- [x] **Integral polynomial Taylor and contraction — current block.** Over any commutative ring, Taylor expansion at \(a+cu\) has one polynomial remainder \(c^2Q(u)\), with \(Q(0)=0\). Over \(\mathbb Z_p\), actual polynomial evaluation is 1-Lipschitz. The map \(u\mapsto c+pH(u)\) has a unique fixed point, which inherits every divisibility bound of \(c\) when \(H(0)=0\).

"""
replace_once("## Clear routes still awaiting formalization", weighted + "## Clear routes still awaiting formalization")
replace_once(
    "| [ ] Next formalization | **Weighted nonlinear lifting and first-order root motion.** | Formalize integral p-adic Taylor estimates, a Jacobian inverse losing at most \\(s\\) digits, and contraction when the residual or perturbation depth exceeds \\(2s\\). The written proof permits a Jacobian singular modulo \\(p\\) but invertible over \\(\\mathbb Q_p\\). |".replace("\\\\", "\\"),
    r"| [ ] Next formalization | **Weighted perturbation and first-order root motion.** | With \(F(a)=0\), \(G=F+p^MH\), \(M>2s\), and \(p^sDF(a)^{-1}\) integral, construct the perturbed root using the original inverse bound and prove \(b-a=-p^MDF(a)^{-1}H(a)+\varepsilon\), \(\varepsilon\in p^{2M-3s}R^d\). The underlying weighted lifting theorem is now checked. |")
replace_once(
    "The checked polynomial statements have integer coefficients and arbitrary p-adic roots and parameters. Continuous polynomial parameter charts are included in this block. General p-adic coefficient interfaces, analyticity, differentiability, and first-order root-motion estimates remain separate.",
    "The new square weighted lifting theorem has arbitrary integral p-adic coefficients and centers. The earlier rectangular chart interfaces retain integer coefficients and integer centers with arbitrary p-adic roots and parameters. Generalizing those interfaces, analyticity, differentiability, and first-order root-motion estimates remain separate.")
replace_once("The new weighted written criterion covers Jacobians invertible over the fraction field.", "The checked weighted criterion covers Jacobians invertible over the fraction field.")
start = checklist.index("## Suggested next block\n")
end = checklist.index("## Evidence locations\n", start)
checklist = checklist[:start] + r"""## Suggested next block

Formalize **weighted perturbation and its first-order remainder** using the now checked integral Taylor and contraction modules. Keep the original Jacobian inverse bound while solving \(F+p^MH=0\), then estimate both the quadratic Taylor contribution and the variation of \(H\). The target error depth is \(2M-3s\). This expansion is a written proof target, not a Lean theorem in the current release.

""" + checklist[end:]
replace_once("## Evidence locations\n", "## Evidence locations\n\n- Current weighted block: `polynomial_weighted/WEIGHTED_LIFTING.md`, `polynomial_weighted/formalization/`, `polynomial_weighted/verification/polynomial_weighted_verification.json`, and `polynomial_weighted/audit/ROUTE_AUDIT.md`.\n")
replace_once("- Latest chart block:", "- Previous chart block:")
(ROOT / "docs/REMAINING_CHECKLIST.md").write_text(checklist)

readme = r"""# Paper IX: weighted nonlinear lifting

**Komorebi P. — 8 September 2026.**

The next weighted lifting block is complete in Lean. Let \(p\) be prime,
\(R=\mathbb Z_p\), \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(J=DF(a)\).
If
\[
J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad
F(a)\in p^rR^d,\qquad r>2s,
\]
then
\[
\boxed{\exists!\,b\in a+p^{s+1}R^d:\ F(b)=0,}
\qquad \boxed{b-a\in p^{r-s}R^d.}
\]
The actual Jacobian can be singular modulo \(p\). Uniqueness is on the full ball
of depth \(s+1\), and the inverse-denominator exponent \(s\) is retained.
The theorem covers arbitrary integral p-adic coefficients and centers, including
the dyadic case and dimension zero. Exact boundary controls show why the strict
threshold and displacement exponent cannot uniformly be improved.

The five new mathematical modules contain 37 theorems and seven definitions.
The proof constructs polynomial Taylor normalization, proves actual polynomial
contraction, retains constant-term precision, and translates the result back to
the original equations. The integral inverse certificate is proved equivalent
to the stated fraction-field hypothesis. Full statements, proof and scope are in
`polynomial_weighted/WEIGHTED_LIFTING.md`.

## Evidence and replay

The fresh verification rebuilds all 30 polynomial mathematical modules and checks
external theorem contracts, positive and negative controls, and all mathematical
declaration axiom closures. Exact counts and hashes are in `RELEASE_AUDIT.json`
and `polynomial_weighted/verification/polynomial_weighted_verification.json`.
Independent review is in `polynomial_weighted/audit/ROUTE_AUDIT.md`.
Development failures and their corrections are retained.

Use the separately supplied pinned Lean 4.34.0-rc2 kit:

    python3 replay_paper9_weighted.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

The runtime and reproducible compiled files are excluded from this source ZIP.
Earlier non-polynomial results retain their recorded historical verification;
they are not all rebuilt by this polynomial gate.

## Cumulative contents

All 1,092 files of the previous parameter-chart release are preserved by exact
uncompressed content hashes. Replaced root documents are retained under
`historical/parameter_charts_release_root/`. The direct coverage map is
`PACKAGE_COMPLETENESS.json`. This includes the previous perturbation, chart,
dyadic sharpening, obstruction, lifting, native, and original completion work.
The previous archive has SHA-256
`063daf6cdaa889c0201735967e015c5f515fe41b57d4e8741ca1b2b977d83d6f`.
Older manuscript recovery limitations and historical statuses remain recorded.

## Remaining work

The next precise target is weighted perturbation and its first-order formula:
for \(F(a)=0\), \(G=F+p^MH\), \(M>2s\),
\[
b-a=-p^MDF(a)^{-1}H(a)+\varepsilon,
\qquad \varepsilon\in p^{2M-3s}R^d.
\]
That expansion remains a written proof awaiting Lean formalization. Prescribed
parameter obstructions, general rank-deficient towers, analyticity, native
presentation invariance and descent, additional exact dyadic valuations and
period families, and manuscript consolidation remain on `REMAINING_CHECKLIST.md`.

The original stated Nishibuchi conjecture and earlier sharp dyadic results remain
completed with their recorded scopes. This release does not assert that every
strengthening or the full native program is resolved.
"""
(ROOT / "docs/README.md").write_text(readme)
print("Prepared README.md and REMAINING_CHECKLIST.md")
