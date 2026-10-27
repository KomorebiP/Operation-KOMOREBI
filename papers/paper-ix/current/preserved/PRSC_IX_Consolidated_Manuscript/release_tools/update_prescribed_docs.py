#!/usr/bin/env python3
"""Prepare the current prescribed-parameter release checklist and overview."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parents[1] / "output/PRSC_IX_Complete_First_Order_Motion.zip"
with zipfile.ZipFile(BASE) as archive:
    checklist = archive.read("PRSC_IX_Complete_First_Order_Motion/REMAINING_CHECKLIST.md").decode()

def replace_once(old, new):
    global checklist
    assert checklist.count(old) == 1, old[:100]
    checklist = checklist.replace(old, new)

replace_once("**Current first-order root-motion block: fresh verification PASS.**", "**Current prescribed-parameter block: fresh verification PASS.**")
replace_once("**Weighted perturbation and first-order root motion — current block.**", "**Weighted perturbation and first-order root motion — preceding block.**")
prescribed = r"""- [x] **Prescribed-parameter polynomial obstruction and exact fibers — current block.** For \(q>0\), \(L\ge1\), \(m\) solved variables, \(k\) parameter variables, \(e\) equations, and an actual lower integer polynomial root \(x\), derive \(r=q^{-L}F(x)\). Let \(J\) and \(K\) be the actual reduced Jacobian blocks. For each prescribed parameter digit \(v\), define
  \[
  \mathcal C_x=(\mathbb Z/q\mathbb Z)^e/\operatorname{im}J,
  \qquad o_x(v)=[\bar r+Kv].
  \]
  The actual next-level residue lifts \(\mathcal L_v\) with that parameter digit satisfy
  \[
  \mathcal L_v\ne\varnothing\iff o_x(v)=0,
  \qquad \mathcal L_v\cong\{u:Ju=-\bar r-Kv\}.
  \]
  Every nonempty fiber is a checked torsor for \(\ker J\), including positive composite moduli. For prime \(p\), put \(\rho=\operatorname{rank}_{\mathbb F_p}J\). Then
  \[
  \#\mathcal L_v=\begin{cases}p^{m-\rho},&o_x(v)=0,\\0,&o_x(v)\ne0,\end{cases}
  \qquad \#\mathcal C_x=p^{e-\rho}.
  \]
  The same derived residual supports all parameter digits. These are counts of actual residue classes. No full-rank assumption is imposed. The criterion includes \(q=1\) and zero dimensions; the rank formulas require a prime field.

"""
replace_once("## Clear routes still awaiting formalization", prescribed + "## Clear routes still awaiting formalization")
lines = checklist.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| [ ] Next formalization | **Prescribed-parameter obstruction."):
        lines[i] = "| [ ] Next formalization | **Compatible towers with prescribed parameters.** | State sufficient hypotheses ensuring that each successive prescribed digit is admissible, construct compatible actual lifts, and pass to the p-adic limit. The one-step obstruction, fiber, and count are now checked. |"
checklist = "\n".join(lines) + "\n"
replace_once("The new square weighted lifting theorem has arbitrary integral p-adic coefficients and centers.", "The square weighted lifting and first-order motion theorems have arbitrary integral p-adic coefficients and centers. The prescribed-parameter finite-lifting theorem uses integer polynomial coefficients and integer lower-root representatives.")
start = checklist.index("## Suggested next block\n")
end = checklist.index("## Evidence locations\n", start)
checklist = checklist[:start] + r"""## Suggested next block

Formalize **compatible polynomial towers with prescribed parameter paths** under explicit sufficient hypotheses. The new theorem tests each proposed next digit exactly. A one-step success does not itself establish persistence at later levels. Begin with a suitable surjective solved-coordinate block and make the actual parameter constraints survive the construction and p-adic limit; retain general singular persistence as a separate question.

""" + checklist[end:]
replace_once("## Evidence locations\n", "## Evidence locations\n\n- Current prescribed-parameter block: `polynomial_prescribed/PRESCRIBED_PARAMETER_LIFTING.md`, `polynomial_prescribed/formalization/`, `polynomial_prescribed/verification/polynomial_prescribed_verification.json`, and `polynomial_prescribed/audit/ROUTE_AUDIT.md`.\n")
replace_once("- Current first-order block:", "- Previous first-order block:")
(ROOT / "docs/REMAINING_CHECKLIST.md").write_text(checklist)

readme = r"""# Paper IX: prescribed-parameter polynomial lifting

**Komorebi P. — 8 September 2026.**

The prescribed-parameter obstruction, actual residue fibers, and exact counts
are complete in Lean. Let \(q>0\), \(L\ge1\), and let an integer polynomial
system \(F(Y,T)\) with \(e\) equations have a lower root \(x\) modulo \(q^L\).
There are \(m\) solved variables and \(k\) prescribed parameter variables.
Write \(r=q^{-L}F(x)\), and let \(J=D_YF(x)\bmod q\), \(K=D_TF(x)\bmod q\).

For a prescribed parameter digit \(v\), the actual next-level residue lift set
\(\mathcal L_v\) satisfies
\[
\boxed{\mathcal L_v\ne\varnothing\iff[\bar r+Kv]=0\text{ in }\operatorname{coker}J.}
\]
There is an explicit equivalence
\[
\mathcal L_v\cong\{u:Ju=-\bar r-Kv\},
\]
and every nonempty fiber is a torsor for \(\ker J\). When \(q=p\) is prime and
\(\rho=\operatorname{rank}_{\mathbb F_p}J\),
\[
\#\mathcal L_v=\begin{cases}p^{m-\rho},&[\bar r+Kv]=0,\\0,&\text{otherwise},\end{cases}
\qquad \#\operatorname{coker}J=p^{e-\rho}.
\]
The residual is derived from the original lower root, uniformly for every
parameter digit. No surjectivity assumption is imposed. The criterion and
torsor cover composite moduli and modulus one; rank counts use prime fields.

The four new mathematical modules contain 16 theorems, ten definitions, and
three abbreviations. Full statements, proof, controls, and boundaries are in
`polynomial_prescribed/PRESCRIBED_PARAMETER_LIFTING.md`. The active checklist is
`REMAINING_CHECKLIST.md`.

## Verification and replay

The fresh gate compiles all 39 mathematical polynomial modules and checks
expanded contracts for actual residue vectors, controls, and every declaration's
axiom closure. Exact counts, hashes and timings are in `RELEASE_AUDIT.json` and
`polynomial_prescribed/verification/polynomial_prescribed_verification.json`.
Independent proof review and reconciliation are under `polynomial_prescribed/audit/`.
Actual failed development attempts and their corrections are retained.

Use the separately supplied pinned Lean 4.34.0-rc2 kit:

    python3 replay_paper9_prescribed.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

The runtime and reproducible compiled outputs are excluded from this source
archive. Earlier non-polynomial proofs retain their recorded historical verification.

## Cumulative contents

All 1,407 files of the preceding first-order motion release are preserved by
exact uncompressed content hashes. Replaced root documents are retained under
`historical/first_order_motion_release_root/`. The exact map is
`PACKAGE_COMPLETENESS.json`. The previous ZIP has SHA-256
`9b0db84f38397e67b7f61fe32b8fa1bf82614324f98703749bc02e2c838ad766`.
This includes the complete first-order formula
\[
b-a=-p^MDF(a)^{-1}H(a)+\varepsilon,\qquad\varepsilon\in p^{2M-3s}\mathbb Z_p^d,
\]
under its stated original inverse bound and \(M>2s\), together with earlier
weighted lifting, continuous charts, dyadic sharpenings, obstruction work,
and original Nishibuchi completion. Historical recovery limitations remain recorded.

## Remaining work

The next clear block is compatible polynomial towers with prescribed parameter
paths under explicit sufficient hypotheses. The one-step criterion alone does
not imply that every later prescribed digit will be admissible.
General rationally rank-deficient towers, higher obstructions, analytic
regularity, native presentation invariance and global/completed descent, further
exact valuation and period questions, and manuscript consolidation remain separate.

The original stated Nishibuchi conjecture retains its completed scope. This
release does not resolve every strengthening or the full native program.
"""
(ROOT / "docs/README.md").write_text(readme)
print("Prepared prescribed-parameter release documents")
