# Continue here — finite-dimensional semantics closed

Read `README.md`, `FINAL_VERIFICATION_RECEIPT.json`, and `PROOF_NOTE.md` first.

## New closed boundary

`Komorebi/FDGaussianConditioning.lean` proves actual joint disintegration,
actual Gaussian evidence, and canonical Bayesian posterior equality for arbitrary
finite real state/observation index types, with `P.PosSemidef` and `R.PosDef`.

This supersedes the OPEN finite-dimensional conditioning boundary of continuation
v2 and the covariance checkpoint. Do not mistake the one-rewrite parameter wrapper
for the main theorem: the main theorem uses both generative joint laws.

## Strongest next block

Connect this theorem to the existing coordinate-free
`BayesianMultiscaleKalmanPosteriorPerturbation.lean` layer.

1. Identify `matrixCLM` of matrix multiplication with continuous-linear-map
   composition and matrix transpose with the adjoint. The adjoint identity is
   already checked in `FDGaussianTransport.lean`.
2. Identify the matrix innovation, gain, and Joseph covariance maps with the
   earlier operator definitions. Derive the inverse operator identities from
   `innovation_inv_mul` and `innovation_mul_inv`; do not posit them as new axioms.
3. Use `covarianceBilin_multivariateGaussian` and the now checked canonical
   posterior theorem to interpret the previous `posteriorCovErrorOp` as the
   covariance-operator discrepancy of actual posterior versions.
4. Attach the existing norm budgets and exact orthogonal descendant refinement
   to those actual covariance operators. Keep the norms consistent. Do not apply
   a Frobenius/Pythagorean identity to an operator norm without a separate proof.
5. Treat two different evidence measures carefully when comparing two canonical
   posterior versions. The explicit Gaussian posterior versions are defined for
   every observation; equality to each canonical kernel holds with respect to its
   own evidence law. Do not silently assume a common null set across different
   models without proving absolute continuity or an equivalent transfer result.

Only after these interfaces check, promote the nontrivial multiscale
posterior-kernel theorem. Then pursue a posterior metric bound.

## Verification protocol

Use `MODULE_ORDER.json`. Keep every Lean invocation separate. Do not replace
this proof by a numerical covariance check. Keep all checked sources free of
placeholders and custom axioms. Recheck final sources with warnings as errors and
repeat the axiom audit after each extension. Preserve source hashes, recorded
failures, and all remaining assumptions.

## Still open

- Full finite-dimensional multiscale perturbation semantic integration.
- Distributional metric estimates driven by the multiscale residual budget.
- Singular innovation/pseudoinverse conditioning and weaker noise assumptions.
- Pointwise normalized multivariate Bayes-density formula, if later needed.
- Itô derivation, nonlinear/non-Gaussian extensions, and literature-priority audit.
