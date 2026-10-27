# Scalar Gaussian Posterior Perturbation Semantic Bridge v0.1.0 — Checked

This release performs the second proof step in the 2026-09-09 Unified Inference/Stochastic/Bayesian continuation plan.

It connects the already checked coordinate-free Kalman posterior perturbation algebra to the already checked arbitrary-scalar Gaussian Bayesian conditioning semantics.

For scalar models

\[
X\sim N(m,p),\qquad Y\mid X=x\sim N(hx,r),
\]

and a second model `(h0,m0,p0,r0)`, the source proves:

- scalar operator realization of `H`, `P`, `R`, `S^{-1}`, `K`, the posterior mean, and Joseph covariance;
- the `posteriorCovErrorOp` used by the multiscale theorem is exactly multiplication by
  `posteriorVar(h,p,r) - posteriorVar(h0,p0,r0)`;
- the checked end-to-end posterior-mean residual budget applies directly to the difference of the Gaussian conditional posterior means;
- the checked end-to-end Joseph posterior-covariance residual budget applies directly to the difference of the Gaussian conditional posterior variances;
- for positive prior/noise variances, the coordinate-free update parameters are those of the explicit Gaussian posterior kernel, that kernel equals Mathlib's canonical posterior evidence-a.e., and the same kernel is the normalized Bayes measure for every fixed observation.

## What this closes

In the scalar linear-Gaussian model, `m+` and `P+` in the perturbation theory are no longer merely algebraic Kalman quantities: they are the mean and covariance parameters of an actual Bayesian conditional-posterior version.

## Boundary

This does **not** make a nontrivial scalar state space into a multiscale spatial decomposition. The abstract coarse/fine projector refinement theorem remains algebraically valid, but genuinely nontrivial multiscale posterior semantics still requires a finite-dimensional (or Hilbert-space) Gaussian conditioning bridge. Finite-dimensional `H` is therefore still **open / not claimed** by this release.

No literature-priority claim is made.

## Verification

Checked in the preserved environment:

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- warnings treated as errors
- zero `sorry`, `admit`, or custom axioms in the checked bridge source
- representative axiom audits: `propext`, `Classical.choice`, `Quot.sound`

`deps/` contains the exact source snapshots imported by the bridge. `scripts/check_in_pinned_runtime.sh` reconstructs their local module artifacts and checks the bridge.
