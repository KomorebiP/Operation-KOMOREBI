# Unified Inference Lean v0.6.0 — Status

## Checked inventory

- 99 theorem declarations
- 54 definitions/abbreviations
- 1 structure
- 0 `sorry`
- 0 `admit`
- 0 custom axiom declarations
- warning-as-error source check: RC=0
- representative axiom audit: RC=0

## New stochastic block

The file now contains a genuine Brownian-driven constant-coefficient affine Itô process

`X_t = x0 + drift * t + vol * B_t`

built from Mathlib's `IsPreBrownianReal` object.  Theorems derive:

1. exact one-time Gaussian law;
2. exact mean `E[X_t] = x0 + drift*t`;
3. exact variance `Var[X_t] = vol^2*t`;
4. exact covariance `Cov(X_s,X_t) = vol^2*min(s,t)`;
5. exact Gaussian law of every increment;
6. exact increment mean and variance;
7. independent increments of the full affine process;
8. independence of the present state from every future increment;
9. exact finite-time mean evolution;
10. exact finite-time variance evolution.

This is a genuine stochastic derivation from Brownian finite-dimensional laws and independence, not a theorem that assumes the moment equations.

## Remaining stochastic boundary

The manuscript's general linear SDE `dX=(AX+b)dt+G dW` is not yet derived in full because the pinned Mathlib environment does not contain a native general stochastic-integral / Itô formula stack.  Current public `formal-mathfin` supplies a richer Itô tower, but its live release is pinned to Lean 4.32 and is not directly build-compatible with this preserved Lean 4.34.0-rc2 environment.  No incompatible external theorem was imported or counted.

The next semantic target is Gaussian conditioning / Kalman Bayes, beginning with an exact scalar density-level conditioning theorem if the multivariate conditioning API is insufficient.
