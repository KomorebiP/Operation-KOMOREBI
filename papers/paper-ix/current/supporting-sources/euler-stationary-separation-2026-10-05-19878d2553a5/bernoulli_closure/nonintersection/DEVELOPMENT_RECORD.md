# Development and verification record

This route began by testing whether the size of the ordinary index alone gives a critical-value upper bound below2r−25. No such bound was obtained. Existing dense-pole and finite-binary-support records were read before choosing a new input; no global analytic interpolation in the multiplier was assumed.

The new input was the actual midpoint Bernoulli function D. Its first terms prove D=1+4z+16R coefficientwise. This yields exact scaled isometry and the2x2 Hankel law. Exact rational exploration of higher Hankel determinants suggested the valuation formula later proved by the authenticated Bernoulli orthogonal recurrence and a unit-norm lattice. No observed finite pattern was promoted to proof.

An initial exploratory command importing Sympy failed with `ModuleNotFoundError: No module named 'sympy'`. It produced no mathematical result. The code was replaced with Python standard-library Fraction arithmetic and an independent Bernoulli recurrence. The delivered checker has no external dependency.

Current completed run: `certified_run/manifest.json`, validated against the current checker. It records36 orthogonality checks,9 unit-norm checks,72 depleted shifted determinant checks,232 actual Bernoulli transfer checks, and three boundary controls. The checks verify the implementation and finite assertions; the universal statement is supported by the separate proof.

No T digits were extended. No Lean run was performed. No actual stationary critical value was declared nonzero from the unweighted Hankel theorem. The remaining bridge is to identify an appropriate bounded-loss Gram or Schur expression for the actual Newton/source-weighted obstruction.
