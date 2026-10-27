# Paper IX: local analytic parameter regularity

**Author: Komorebi P. — 8 September 2026.**

This cumulative release closes both local analyticity and differentiability
of the polynomial parameter solution map.

Let \(F\in\mathbb Q_p[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\),
\(a=(y_0,t_0)\), and \(F(a)=0\). Put \(J=D_YF(a)\), \(K=D_TF(a)\).
If \(J\in\operatorname{GL}_e(\mathbb Q_p)\), there exist open neighborhoods
\(t_0\in U\subseteq\mathbb Q_p^k\), \(y_0\in V\subseteq\mathbb Q_p^e\),
and a map \(\psi:\mathbb Q_p^k\to\mathbb Q_p^e\), analytic near every
point of \(U\), such that
\[
\psi(t_0)=y_0,\qquad\psi(U)\subseteq V,\qquad
F(y,t)=0\iff y=\psi(t)\quad(t\in U,\ y\in V),
\]
\[
\boxed{D\psi(t_0)=-J^{-1}K.}
\]
Lean certifies the stronger strict Fréchet derivative statement. The actual
formal partial derivatives are proved to be the analytic derivative, and
the actual augmented polynomial system supplies the inverse. No analyticity,
derivative formula, or preselected solution map is assumed in the main theorem.

Every continuous local root selection through the same nonsingular point
has this analytic germ and this derivative. On an open parameter set, a
continuous exact root selection with invertible solved Jacobian at every
point is analytic throughout, with the actual implicit derivative at each point.

The core works over every complete nontrivially normed field. The p-adic
specialization includes every prime, including 2, and arbitrary finite
dimensions, including zero. An explicit theorem handles integral p-adic
coefficients and centers in the ambient field \(\mathbb Q_p\).

## Proof and scope

The proof applies the analytic inverse theorem to \((F(Y,T),T)\).
Its derivative and inverse are
\[
\begin{pmatrix}J&K\\0&I\end{pmatrix},\qquad
\begin{pmatrix}J^{-1}&-J^{-1}K\\0&I\end{pmatrix}.
\]
Restrict the local inverse to targets \((0,t)\), project to the solved
coordinates, and extract an open product neighborhood. This gives both
directions of the local root characterization.

The analytic neighborhoods have no newly asserted explicit uniform radius.
The earlier weighted existence radii and quantitative error estimates remain
valid separate results. Analyticity is local; no claim is made on all of
\(\mathbb Q_p^k\). The integral specialization produces a field-valued
analytic branch, and does not treat \(\mathbb Z_p\) as a vector space over
\(\mathbb Q_p\). No new identity with every historical subtype-valued chart
is claimed.

## Evidence

The fresh cumulative gate passed **91 checks**, including **55 mathematical modules** and **515 project declaration axiom closures**. All 49 inherited mathematical modules are unchanged. Six new mathematical modules add **30 theorems and 8 definitions**. Source hashes, commands and logs are recorded in `polynomial_regularity/verification/polynomial_regularity_verification.json`.

The controls include the actual linear system \(F(Y,T)=Y+T\), its unique
root \(y=-t\), its analytic branch and derivative, rejection of the wrong
positive derivative sign, and an actual nonlinear invocation of the theorem.
Development proof-script failures and fixes are retained in `dev/`; the
independent raw-source review is separate from compiler acceptance.

- Mathematical exposition: `polynomial_regularity/ANALYTIC_REGULARITY.md`.
- Main theorem: `Komorebi.PolynomialAnalyticImplicit.exists_analytic_implicit`.
- Integral theorem: `Komorebi.PolynomialRegularityIntegral.exists_analytic_integral_implicit`.
- Selection transfer: `Komorebi.PolynomialAnalyticSelection.continuous_selection_regularity`.
- Independent audit: `polynomial_regularity/audit/`.
- Full proved/open checklist: `REMAINING_CHECKLIST.md`.
- Reproduction: `replay_paper9_regularity.py --kit PATH --output EMPTY_DIRECTORY`.

Reproduction uses the separately supplied pinned Lean 4.34.0-rc2 and Mathlib
runtime recorded by the verifier. The compatibility adapter restores executable
path discovery. Allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`.

## Preserved work and remaining questions

Every file in the preceding **1,971-file joint-deformation archive** is
retained with identical content. Replaced root documents are moved to a
historical folder; `PACKAGE_COMPLETENESS.json` records every old-to-new mapping.
The previous archive SHA-256 is
`646a19a95af884cb4e7373ac97298c7a81ef25589eba56181a6157d43ca4eed0`.

This preserves the original Nishibuchi completion, dyadic sharpenings and
edge towers, finite obstructions, counts, smooth and prescribed-parameter
towers, continuous charts, weighted lifting, and joint deformation.
Earlier non-polynomial proofs retain their historical verification; this
gate recompiles the polynomial development. Historical recovery limitations
remain recorded.

General rationally rank-deficient singular persistence, native presentation
invariance, global/completed descent, sharper arithmetic, historical formula
recovery, and manuscript consolidation remain unfinished. The original
stated Nishibuchi conjecture retains its completed scope. This release closes
the local regularity block, not the entire strengthening or native program.
