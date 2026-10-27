# Adversarial self-review

Original target: U_Gamma=U_alg, using the previously fixed complex branch.
Not proved in this block.

1. Tested the dangerous one-sided Fourier antiderivative: its opposite endpoint
   need not decay unless the full orbit sum vanishes. Both tails are retained.
2. Verified the transpose action, not the inverse action under an unstated
   convention: h composed with M has coefficient b_(M^{-T}k).
3. Checked that every nonzero integer frequency escapes in both directions.
   This follows from hyperbolicity and lattice discreteness, not numerical roots.
4. Checked the global holomorphic claim: superexponential coefficient estimates
   on every product annulus and the expanding-tail choice give normal convergence.
5. A multiplier may have nonzero winding. It is kept as an integer monomial;
   division by three is not applied to an arbitrary logarithm.
6. Based ratios, not raw unit coefficients, remove the independent scalar alpha.
7. Conjugation symmetry of orbit sums is weaker than their vanishing. The
   original known modulus is used only after identifying the actual discrepancy
   with the based ratio. No gamma/model identification is inferred from the
   abstract construction.
8. The raw F(pi(v)) is not periodic on X. Substituting its one-variable series
   for a nonexistent relative scalar Laurent expansion would be invalid.
9. The finite solver accepts certified orbit stretches; it does not use bounded
   searches to decide global orbit equivalence of arbitrary integer seeds.
10. The finite-period counterexample works for every prescribed N by an adjugate
    denominator argument. Only its N<=6 coefficient instances are executed.

Review status: mathematical self-review, exact independent code paths for
matrices/polynomials, and Lean coefficient checking. No independent researcher
or separate-agent analytic review is claimed.

Next actual work: derive a nonzero smooth relative multiplier from the gamma
and arithmetic-model data; retain cancellations of poles and zeros; identify
its based value; compute the conjugation-asymmetric Fourier orbit sums by an
exact generating function or reindexing theorem. All remain open here.
