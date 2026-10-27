# Polynomial roots under coefficient perturbation

Komorebi P. — 8 September 2026

This block formalizes square root uniqueness and nearby-root stability for finite systems of integer polynomials. The polynomials and their partial derivatives are evaluated directly. No root-uniqueness or perturbation-stability premise is assumed.

## Notation

Let \(p\) be prime, \(L\ge1\), and
\[
F,H\in\mathbb Z[X_1,\ldots,X_d]^e,
\qquad x\in\mathbb Z^d.
\]
Write
\[
A_x=DF(x)\bmod p:\mathbb F_p^d\longrightarrow\mathbb F_p^e,
\qquad B_L(x)=x+p^L\mathbb Z_p^d.
\]
For an integer \(c\), the perturbed system is the actual polynomial list
\[
G=F+cH.
\]
There is no restriction on the sign of \(c\), and \(c=0\) is allowed. Divisibility conclusions give lower bounds on precision and allow zero differences.

## 1. Unique roots for square systems

If \(d=e\), \(A_x\) is surjective, and \(F(x)\equiv0\pmod{p^L}\), then
\[
\boxed{\exists!\,a\in B_L(x):F(a)=0.}
\]
The stronger comparison lemma proves that any two exact roots of \(F\) in \(B_L(x)\) coincide, without needing a separate lower-root hypothesis.

**Proof implemented.** Map every arbitrary p-adic root into the actual residue rings \(\mathbb Z/p^n\mathbb Z\), and choose its canonical integer representative. Evaluation commutes with reduction, so these representatives are genuine finite polynomial roots. The preceding count theorem gives exactly \(p^{d-d}=1\) next-level residue lift. Inductively any two roots agree at every precision. The p-adic residue maps separate points, so the roots are equal. Existence is the preceding checked tower theorem.

This extends uniqueness from the limit of a selected sequence to **all exact roots in the prescribed ball**.

## 2. Coefficient perturbations preserve smooth liftability

If \(p^L\mid c\), the actual identities give
\[
G(x)=F(x)+cH(x),\qquad DG(x)\equiv DF(x)\pmod p.
\]
Thus if \(F(x)\equiv0\pmod{p^L}\) and \(A_x\) is surjective, then
\[
\exists b\in B_L(x):G(b)=0.
\]
This theorem allows rectangular systems. The evaluation, derivative and Jacobian identities are proved from the polynomial definition \(G_i=F_i+C(c)H_i\), rather than supplied as hypotheses. Algebraic congruence helpers also permit composite moduli; exact p-adic root existence uses prime \(p\).

## 3. Nearby roots for rectangular systems

Let \(M\ge1\) and \(p^M\mid c\). Suppose \(A_x\) is surjective and \(a\in\mathbb Z_p^d\) is an exact root of \(F\) with \(a\equiv x\pmod p\). Then
\[
\boxed{\exists b\in\mathbb Z_p^d:\quad G(b)=0,
\qquad b\equiv a\pmod{p^M}.}
\]
No uniqueness is claimed when \(d>e\).

**Proof implemented.** Truncate \(a\) to an integer vector \(y\) modulo \(p^M\). It is an actual lower root of \(F\), and its reduced Jacobian agrees with \(A_x\). Apply the coefficient-perturbed existence theorem at precision \(M\), then combine the two congruences through \(y\).

## 4. Full precision for the unique square root

Suppose \(d=e\), \(M\ge L\ge1\), \(p^M\mid c\), and \(A_x\) is surjective. If
\[
a,b\in B_L(x),\qquad F(a)=0,\qquad G(b)=0,
\]
then
\[
\boxed{b-a\in p^M\mathbb Z_p^d.}
\]
In particular, for \(G=F+p^MH\), no p-adic digits below depth \(M\) are changed in the selected root.

The formalization also proves a combined existence theorem. Starting only with \(F(x)\equiv0\pmod{p^L}\), it constructs an original root \(a\in B_L(x)\) and proves that there is exactly one \(b\in B_L(x)\) satisfying \(G(b)=0\) and \(b\equiv a\pmod{p^M}\). The comparison theorem shows that the precision bound holds for every root of \(G\) in that ball, so uniqueness is not obtained merely by adding a restrictive displacement condition.

**Proof implemented.** Section 3 produces a nearby root \(b'\). Since \(M\ge L\), it belongs to \(B_L(x)\). The perturbed Jacobian remains surjective, and square uniqueness identifies \(b'\) with the arbitrary root \(b\).

## Formal source map

| Source | Contents |
|---|---|
| `PolynomialPadicUnique.lean` | Residue quotient/divisibility equivalence, integer truncation, root reduction, one-child comparison, arbitrary-root uniqueness, unique existence |
| `PolynomialCoefficientPerturbation.lean` | Actual coefficient perturbation, evaluation and derivative identities, reduced Jacobian preservation, preserved lower roots and p-adic existence |
| `PolynomialRootStability.lean` | Common-residue helper, rectangular nearby-root existence, square root comparison, unique nearby root and combined existence |

These three new modules contain **24 declarations: 21 theorems and 3 definitions**. Counts of control lemmas, contracts, and inherited declarations are reported separately by the fresh gate. They must not be added as if they were distinct mathematical discoveries.

## Exact boundaries

- The new theorems include \(p=2\), \(L=M\), \(c=0\), negative perturbation scalars, and zero variable/equation dimensions where their types permit them.
- The coefficient lists are integer polynomials. The roots are arbitrary actual p-adic vectors. An interface quantifying over arbitrary p-adic coefficients or parameter specializations remains to be formalized.
- Uniqueness concerns a square system in a chosen smooth residue ball. It does not hold across every residue ball or for general rectangular systems.
- The guaranteed perturbation depth is \(M\). It is not generally \(M+1\): \(F(X)=X\), \(H=-1\), \(p=2\), \(M=1\) moves the root from 0 to 2.
- Weighted nonunit-Jacobian lifting, the first-order displacement expansion, and continuous parameter charts have written proofs in `research/perturbation/Paper_IX_Perturbation_Deformation_Bridge.md`. Their additional p-adic Taylor, inverse, and parameter interfaces are not formalized by this block.
- General singular deformation problems, native presentation invariance and global descent remain separate.

## Verification

The authoritative fresh report is `verification/polynomial_deformation_verification.json`. The replay compiles all required project modules into a new directory, with warnings treated as errors, verifies expanded statement contracts, prints the axiom dependencies of every inventoried declaration, and rejects three invalid extensions. Only `propext`, `Classical.choice` and `Quot.sound` are allowed. The pinned Lean/Mathlib cache is reused; project compiled outputs are rebuilt.

The independent proof audit and its source/report reconciliation accompany the gate. Development logs retain failed elaboration attempts as well as the passing builds. A failing development attempt is not represented as a proved theorem.

## Next formalization

Use the root stability theorem to specialize polynomial parameter families. After choosing an invertible Jacobian minor, first fix integer free coordinates, then use controlled p-adic approximations and stability to pass to arbitrary p-adic free coordinates. This is the direct route to the continuous rectangular root graph already proved in the written perturbation note. The weighted inverse and Taylor route handles the additional nonunit-Jacobian branch.
