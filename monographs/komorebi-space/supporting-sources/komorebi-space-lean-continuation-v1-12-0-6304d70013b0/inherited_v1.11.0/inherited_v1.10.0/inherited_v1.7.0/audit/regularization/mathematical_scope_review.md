# Written extension hypothesis review — 1.5.0

The new WR catalogue is separate from KS01–KS80. This is a written mathematical review, not an executable proof checker.

**WR01.** The correction space is a real Hilbert space, and the operator is bounded and linear. A uniform bound applies to the actual correction norm. The weak subsequence lemma is proved within the manuscript, using a countable basis of the separable closed span of the sequence. Its consequence is existence, not strong convergence of arbitrary candidates. The orthonormal-sequence counterexample is retained.

**WR02.** Every finite constraint set is nonempty, closed, affine, and nested in the same Hilbert space. The candidates are the minimum-norm points. Their affine direction spaces yield the exact Pythagorean identity. Bounded minimum norms are equivalent to a nonempty intersection and imply strong convergence. A convex-but-not-affine counterexample rejects the stronger equality claim.

**WR03–WR04.** The budget is finite and nonnegative, and its norm is the inherited correction norm. Weak sequential compactness proves attainment. The image of a closed ball is norm closed by the lifting argument even if the full range is not. The dual formula uses the adjoint of the restricted operator. It handles zero budget, zero residual, and zero restricted adjoint. The support inequality follows by differentiating a segment in the feasible ball, not by an unjustified minimax interchange.

**WR05.** Both compared maps act on the same protected Hilbert kernel. The error term is delta + eta*M. A perturbation of the preservation map is not covered. A positive robust lower bound rules out the whole specified budget ball; disappearance of that lower bound is not a feasibility theorem.

**WR06–WR07.** Alpha is strictly positive. Coercivity, closed range, and self-adjointness construct the inverse, including in infinite dimension. The quadratic energy identity proves uniqueness. Nonorthogonal kernel coordinates retain their Gram matrix. The supplied finite program returns both fit and actual candidate residuals and an exact unnormalized budget witness. Squared norms remain rational; normalization is specified symbolically rather than rounded.

**WR08.** Let b be the projection onto the closure of the range. Strong convergence requires b in the actual range, not simply closure membership. Otherwise correction norms diverge. A positive orthogonal floor may coexist with either convergence or divergence. Vanishing weighted penalty alpha*||a_alpha||^2 does not bound ||a_alpha||.

**WR09.** The forward and preservation maps stay fixed. The universal coefficient 1/(2*sqrt(alpha)) follows by completing a square and is attained by a scalar example. Noisy convergence additionally requires attained b, alpha tending to zero, and delta/sqrt(alpha) tending to zero.

**WR10.** The diagonal formulas belong to ell2 for every positive integer m. Infinite tails are controlled by integral inequalities, not truncated numerical inference. Rational programs evaluate finite sums and add the proved bounds for omitted terms.

**WR11.** Riemann sums on a bounded interval are supplemented by uniform tail estimates before passing to the infinite integral. The two integrals are pi/4. Strictly increasing natural budgets and a ratio tending to one permit a monotonic squeeze at arbitrary intermediate budgets. The finite graph uses different natural budget sequences; only the proved limiting statement compares matched budgets. The factor pi/4 is specific to this diagonal datum, not a general optimization advantage.

**WR12.** The changed datum 1/n^2 has the actual Hilbert preimage 1/n. The ceiling parameter rule uses 0<delta<=1. The claimed deterministic rate is a sufficient upper bound, not minimax or statistical optimality. The same rule cannot create an exact solution for the escaping datum.

No new Lean source, imported axiom, or placeholder is introduced. All twelve proofs remain explicit future formalization targets. The old five KS54–KS58 obligations are not reopened.
