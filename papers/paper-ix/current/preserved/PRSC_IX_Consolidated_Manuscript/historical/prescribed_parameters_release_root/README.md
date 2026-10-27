# Paper IX: prescribed-parameter polynomial lifting

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
