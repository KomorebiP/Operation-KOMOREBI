#!/usr/bin/env python3
"""Update Paper IX's checklist for the certified first-order motion block."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1] / "output/PRSC_IX_Complete_Weighted_Lifting.zip"
with zipfile.ZipFile(BASE) as archive:
    checklist = archive.read("PRSC_IX_Complete_Weighted_Lifting/REMAINING_CHECKLIST.md").decode()

def replace_once(old, new):
    global checklist
    assert checklist.count(old) == 1, old[:100]
    checklist = checklist.replace(old, new)

replace_once("**Current weighted lifting block: fresh verification PASS.**", "**Current first-order root-motion block: fresh verification PASS.**")
replace_once("**Weighted nonlinear lifting — current block.**", "**Weighted nonlinear lifting — preceding block.**")
replace_once("**Integral polynomial Taylor and contraction — current block.**", "**Integral polynomial Taylor and contraction — preceding block.**")
motion = r"""- [x] **Weighted perturbation and first-order root motion — current block.** For prime \(p\), let \(R=\mathbb Z_p\), \(F,H\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), \(F(a)=0\), and \(J=DF(a)\). Suppose \(J\in\operatorname{GL}_d(\mathbb Q_p)\), \(p^sJ^{-1}\in M_d(R)\), and \(M>2s\). Then \(G=F+p^MH\) has exactly one root \(b\) in \(a+p^{s+1}R^d\), with
  \[
  b-a\in p^{M-s}R^d,\qquad
  b-a=-p^MJ^{-1}H(a)+\varepsilon,\qquad
  \varepsilon\in p^{2M-3s}R^d.
  \]
  The Jacobian is the original one. Root construction, full-ball uniqueness, and the integral error vector are all supplied by the theorem. The dyadic quadratic control realizes error depth exactly \(2M-3s\), so an extra digit cannot uniformly be guaranteed. This includes arbitrary p-adic coefficients and centers, every prime, and finite square dimension.

"""
replace_once("## Clear routes still awaiting formalization", motion + "## Clear routes still awaiting formalization")
lines = checklist.splitlines()
lines = [line for line in lines if not line.startswith("| [ ] Next formalization | **Weighted perturbation and first-order root motion.")]
checklist = "\n".join(lines) + "\n"
replace_once("| [ ] Further formalization | **Prescribed-parameter obstruction.**", "| [ ] Next formalization | **Prescribed-parameter obstruction.**")
replace_once("Generalizing those interfaces, analyticity, differentiability, and first-order root-motion estimates remain separate.", "Generalizing those rectangular interfaces, analyticity, and differentiability remain separate. The first-order root-motion estimate is now checked for square systems.")
start = checklist.index("## Suggested next block\n")
end = checklist.index("## Evidence locations\n", start)
checklist = checklist[:start] + r"""## Suggested next block

Formalize **the prescribed-parameter obstruction**. For a split actual Jacobian \((J\ K)\), residual digit \(\bar r\), and prescribed parameter digit \(v\), prove that an actual next-level polynomial lift exists exactly when \([\bar r+Kv]=0\) in \(\operatorname{coker}J\). Connect the solved-digit fiber to \(Ju=-\bar r-Kv\), and distinguish a one-step criterion from any additional compatible-iteration theorem.

""" + checklist[end:]
replace_once("## Evidence locations\n", "## Evidence locations\n\n- Current first-order block: `polynomial_motion/FIRST_ORDER_ROOT_MOTION.md`, `polynomial_motion/formalization/`, `polynomial_motion/verification/polynomial_motion_verification.json`, and `polynomial_motion/audit/ROUTE_AUDIT.md`.\n")
replace_once("- Current weighted block:", "- Previous weighted block:")
(ROOT / "docs/REMAINING_CHECKLIST.md").write_text(checklist)

readme = r"""# Paper IX: weighted first-order root motion

**Komorebi P. — 8 September 2026.**

The first-order perturbation block is complete in Lean. Let \(p\) be prime,
\(R=\mathbb Z_p\), \(F,H\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(F(a)=0\).
Write \(J=DF(a)\). If
\[
J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad M>2s,
\]
then \(G=F+p^MH\) has exactly one root \(b\in a+p^{s+1}R^d\), and
\[
b-a\in p^{M-s}R^d,\qquad
\boxed{b-a=-p^MJ^{-1}H(a)+\varepsilon,\quad \varepsilon\in p^{2M-3s}R^d.}
\]
The proof constructs the root using the original Jacobian bound. It covers all
primes, arbitrary integral p-adic coefficients and centers, and finite square
dimension. Uniqueness holds throughout the stated ball. A checked dyadic
quadratic example realizes the error exponent exactly.

The five new mathematical modules contain 13 theorems and one definition.
The full theorem, proof, sharpness, and scope are in
`polynomial_motion/FIRST_ORDER_ROOT_MOTION.md`. The complete current checklist
is `REMAINING_CHECKLIST.md`.

## Verification and replay

The fresh gate rebuilds all 35 mathematical polynomial modules, checks expanded
theorem statements and boundary controls, and audits every project declaration's
axiom closure. Exact counts, hashes, and provenance are in `RELEASE_AUDIT.json`
and `polynomial_motion/verification/polynomial_motion_verification.json`.
The independent raw proof review and reconciliation are under
`polynomial_motion/audit/`. Actual development failures and corrections are retained.

With the separately supplied pinned Lean 4.34.0-rc2 kit, run:

    python3 replay_paper9_motion.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

Compiled outputs and the separate runtime are excluded from this source archive.
Earlier non-polynomial proofs retain their recorded historical verification.

## Cumulative contents

All 1,248 files of the preceding weighted-lifting release are preserved by
uncompressed content hash. Replaced root documents are under
`historical/weighted_lifting_release_root/`. The exact coverage map is
`PACKAGE_COMPLETENESS.json`. The preceding ZIP has SHA-256
`dd99a705b933eff4fb8305afa6ebe4bcf8bc70812f0178ab76050c57d3e7efce`.
Earlier manuscript recovery limitations and historical source statuses remain recorded.

## Remaining work

The next clear block is the prescribed-parameter obstruction and its bridge to
actual polynomial lifts: \(Ju=-\bar r-Kv\), equivalently
\([\bar r+Kv]=0\) in \(\operatorname{coker}J\).
General rationally rank-deficient towers, higher obstructions, analytic
regularity, native presentation invariance and global/completed descent, further
exact dyadic valuations and period families, and manuscript consolidation remain.

The original stated Nishibuchi conjecture and earlier sharp dyadic results
retain their completed scopes. This release does not resolve every strengthening
or the full native program.
"""
(ROOT / "docs/README.md").write_text(readme)
print("Prepared first-order motion release documents")
