# Strongest next step

## Closed here

Read `PROOF_NOTE.md` and `Komorebi/FDPosteriorCertificate.lean`.
The finite-dimensional semantic integration is now closed: actual centered
posterior covariance equals the existing Joseph operator, actual mean equals
the operator mean update, inverse hypotheses are derived, and both residual
budgets and exact multiscale refinement apply to the actual posterior moments.

Use `GaussianModel`, `posteriorLaw`, `centeredCovOp`, `posteriorCovDiscrepancy`,
`meanErrorBudget`, and `covarianceErrorBudget`. Do not replace centeredCovOp with
Mathlib's uncentered covarianceOperator. Keep the explicit-version versus
canonical-evidence-a.e. distinction.

## Next major open theorem: a shared-noise posterior coupling

For certified factors P=L Lᵀ and R=B Bᵀ, build the posterior sampler

    Z_y = a(y) + (I-KH)L ξ - K B ζ,

where ξ and ζ are independent standard Gaussian vectors. Reuse the checked
Gaussian affine-image and Joseph covariance theorems to prove its law is the
actual explicit posterior. Couple two models with common ξ,ζ and prove the
exact quadratic cost

    E||Z_y-Z0_y0||² = ||a(y)-a0(y0)||²
      + ||(I-KH)L-(I-K0H0)L0||_F² + ||K B-K0 B0||_F².

Then obtain a Wasserstein-2 upper bound from this actual coupling. This is not
yet Lean-checked. The full Gaussian optimal-Wasserstein formula is not required
for an upper bound. Factors must have compatible latent dimensions; factor
mismatch is not automatically a covariance mismatch bound.

After the cost theorem, resolve Frobenius/Hilbert-Schmidt energy using genuinely
self-adjoint complete orthogonal projectors. Do not import an operator-norm
Pythagorean identity. The cost is for a specified coupling, not automatically
an additive decomposition of optimal Wasserstein distance.

## Execution and integrity

Use MODULE_ORDER.json and verify_blocks.py, one heavy module per invocation.
The runtime is Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Do not import PREDECESSOR's monolithic perturbation file together with its split
modules. The dependency slices preserve its needed statements and proof bodies.
Preserve successful source hashes, actual process receipts, and all proof
boundaries. Numerical checks are diagnostic, not theorem certificates.
