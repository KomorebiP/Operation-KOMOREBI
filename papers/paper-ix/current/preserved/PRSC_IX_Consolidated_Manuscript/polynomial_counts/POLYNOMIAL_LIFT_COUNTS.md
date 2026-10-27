# Paper IX: correction torsors and exact polynomial lift counts

**Author: Komorebi P. — 8 September 2026.**

This block formalizes the correction-digit torsor and prime-field counts from the previous checklist. The counts apply to distinct next-level residue classes satisfying the actual polynomial equations. They do not count integer representatives, of which there can be infinitely many.

## The theorem

Let \(p\) be prime, \(L\ge1\), and
\[
F\in\mathbb Z[X_1,\ldots,X_d]^e,
\qquad x\in\mathbb Z^d,
\qquad F(x)\equiv0\pmod{p^L}.
\]
Write
\[
r_x=F(x)/p^L,\qquad b_x=r_x\bmod p,
\qquad A_x=DF(x)\bmod p:\mathbb F_p^d\longrightarrow\mathbb F_p^e,
\qquad \rho_x=\operatorname{rank}_{\mathbb F_p}A_x.
\]
The actual lift set is
\[
\mathcal L_{x,L}=
\left\{y\in(\mathbb Z/p^{L+1}\mathbb Z)^d:
 y\equiv x\pmod{p^L},\quad F(y)=0\right\},
\]
where polynomial evaluation in the displayed set is modulo \(p^{L+1}\). Define
\[
\mathcal O_x=\mathbb F_p^e/\operatorname{im}A_x,
\qquad o_x=[b_x].
\]
Lean proves
\[
\boxed{
\#\mathcal L_{x,L}=
\begin{cases}
p^{d-\rho_x},&o_x=0,\\
0,&o_x\ne0,
\end{cases}
\qquad
\#\mathcal O_x=p^{e-\rho_x}.
}
\]
These formulas permit singular Jacobians and zero variables or zero equations. Nonsingularity is not assumed. In particular, rank alone gives the size of a nonempty lift fiber; the residual obstruction determines whether it is empty.

## Why these are actual residue-class counts

For every positive integer \(q\), including composite moduli and modulus one, and every \(L\ge0\), the checked map
\[
\Phi_{x,L}:(\mathbb Z/q\mathbb Z)^d\longrightarrow
\{y\bmod q^{L+1}:y\equiv x\pmod{q^L}\},
\qquad t\longmapsto x+q^L\widetilde t
\]
is a bijection. Here \(\widetilde t\) is the canonical integer representative of the digit vector. The entire residue fiber therefore has \(q^d\) elements. Injectivity is proved by cancelling \(q^L\) in the corresponding integer divisibility statement; surjectivity comes from the lower-residue congruence.

The formal type `ActualLifts` is a subtype of these genuine `ZMod (q^(L+1))` residue vectors. Its polynomial predicate is evaluated on canonical integer representatives and tested for divisibility by \(q^{L+1}\). The checked polynomial congruence theorem makes that predicate independent of the integer representative. Thus using canonical representatives does not discard or duplicate residue classes.

At positive depth, the preceding actual multivariable Taylor theorem gives
\[
F(x+p^L\widetilde t)\equiv
p^L(r_x+DF(x)\widetilde t)\pmod{p^{L+1}}.
\]
The new bridge proves that the evaluated integer Jacobian reduces to the actual \(\mathbb F_p\)-linear map \(A_x\). Restricting \(\Phi_{x,L}\) therefore gives an explicit equivalence
\[
\boxed{\{t\in\mathbb F_p^d:b_x+A_xt=0\}\simeq\mathcal L_{x,L}.}
\]
The proof uses the actual formal partial derivatives of the original polynomial list.

## The torsor

Let \(\mathcal T_x=\{t:b_x+A_xt=0\}\). Its natural kernel action is
\[
k\cdot t=k+t,\qquad k\in\ker A_x.
\]
For every pair \(u,t\in\mathcal T_x\), exactly one kernel vector sends \(u\) to \(t\), namely \(t-u\). Thus every nonempty correction fiber is a torsor for \(\ker A_x\). Choosing one valid digit \(u\) gives
\[
\mathcal T_x\simeq\ker A_x,
\qquad t\longmapsto t-u.
\]
Lean constructs an explicit `AddTorsor` structure for the digit fiber, proves the unique translation property, and supplies a chosen-point equivalence from the actual residue lift set to the kernel. A basepoint is required for this equivalence, but the translation action itself does not depend on choosing one.

The torsor and residue bijection remain valid over every positive modulus at positive polynomial depth. The displayed powers involving vector-space rank are restricted to prime moduli.

## Connecting the old obstruction to the new count

The earlier obstruction used the integer-domain map
\[
J_x=\rho_p\circ DF(x):\mathbb Z^d\to\mathbb F_p^e.
\]
The new count uses \(A_x:\mathbb F_p^d\to\mathbb F_p^e\). Reduction of integer vectors onto finite vectors is surjective, so the two maps have the same image after restricting scalars. Lean constructs a class-preserving integer-linear equivalence
\[
\mathbb F_p^e/\operatorname{im}J_x
\simeq
\mathbb F_p^e/\operatorname{im}A_x.
\]
Consequently the cardinality theorem counts the original obstruction group, preserving its distinguished residual class. It is not merely a formula for a separately introduced comparison object.

Rank-nullity gives \(\dim\ker A_x=d-\rho_x\), and the quotient dimension is \(e-\rho_x\). Cardinalities of finite vector spaces complete both formulas.

## Verification and boundaries

The active sources, expanded contracts and negative controls are listed in `inventory.json`. The final run is recorded in `verification/polynomial_counts_verification.json`; `INDEPENDENT_PROOF_AUDIT.md` checks the mathematical statement, actual residue interpretation and machine evidence. Only the standard axioms `propext`, `Classical.choice` and `Quot.sound` are permitted. Warnings are treated as errors.

The prime and positive-depth hypotheses matter. At depth zero, \(F=X^2\), \(p=2\), \(x=0\) has zero Jacobian but only one root modulo two, rather than the two predicted by applying the positive-depth rule. Over \(\mathbb Z/4\mathbb Z\), multiplication by two has a kernel of size two, so a general vector-space rank formula with powers of four is inappropriate. These examples explain the scope; the independent audit distinguishes explanatory examples from formally compiled controls.

The compiled controls contrast nonsingular, zero-equation, singular liftable and singular obstructed systems. Earlier failed development attempts, including declaration reducibility, decidability and tactic issues, are preserved separately from the final gate. No mathematical premise was weakened to obtain a pass.

## What this closes and what remains

The fixed-presentation polynomial package now includes actual Taylor transport, a finite obstruction and its representative independence, shared one-step compatibility, correction torsors, the exact number of distinct one-step lifts, and the exact obstruction cardinality.

These are still one-step results. The next clear block is to formalize lifting through all levels under a surjective reduced Jacobian, using its stability along the fixed residue class, and then construct the compatible p-adic limit. General native presentation invariance and global descent still need their own definitions and proof obligations. Exact higher-difference and Mahler-kernel valuation questions are separate and remain open in the project.
