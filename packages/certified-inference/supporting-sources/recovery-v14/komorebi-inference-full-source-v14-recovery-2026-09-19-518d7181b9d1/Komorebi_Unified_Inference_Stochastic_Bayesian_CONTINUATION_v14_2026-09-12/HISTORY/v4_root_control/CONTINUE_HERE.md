# Komorebi Unified Inference / Stochastic / Bayesian — v4

Checkpoint: 2026-09-11 (America/Chicago).

## Active verified layer

`CHECKED_RELEASES/FD_Multiscale_Posterior_Semantic_Bridge_v0.1.0_Checked`

Read its `CONTINUE_HERE.md`, `PROOF_NOTE.md`, and `FINAL_VERIFICATION_RECEIPT.json`.
The finite-dimensional multiscale posterior **moment** semantic bridge is now
CLOSED_CHECKED. The new layer contains 38 modules and 138 theorem/lemma declarations,
including 48 new declarations. All 138 passed the axiom audit. Counts include support
identities and six new symbolic regression theorems, not independent discoveries.

The central theorem is
`Komorebi.FiniteDimensionalGaussianKalman.GaussianModel.multiscale_posterior_certificate`.
It proves actual posterior expectation and centered covariance norm bounds, exact
coarse-to-fine covariance-error refinement, the zero-descendant criterion, and a
contractive coarse-block bound. It assumes valid Gaussian model data, not the
posterior error bound or inverse equations it needs to prove.

Both prior covariances may be singular. Both observation-noise covariances are
positive definite. Matrix action is transported to genuine Euclidean Hilbert-space
continuous linear maps. `centeredCovOp` comes from `covarianceBilin`, not the pinned
library's uncentered `covarianceOperator`.

## Strongest next open block

Prove a distribution-level shared-noise coupling certificate. With compatible
latent dimensions, factors P=L Lᵀ and R=B Bᵀ, and independent standard Gaussian
vectors ξ and ζ, define

    Z_y = a(y) + (I-KH)L ξ - K B ζ.

First prove its law equals the already checked posterior version. Use the same
ξ and ζ for the comparison model. Prove the exact mean-square coupling cost

    ||a(y)-a0(y0)||²
      + ||(I-KH)L-(I-K0 H0)L0||_F²
      + ||K B-K0 B0||_F².

Then turn that cost into a Wasserstein-2 upper bound. None of these coupling or
metric statements is presently marked checked. Do not replace the requested
probability law by a matrix algebra surrogate.

## Boundaries that must remain explicit

- Factor discrepancies do not automatically equal covariance discrepancies.
- Frobenius/Hilbert-Schmidt packet square sums require appropriate self-adjoint
  orthogonal geometry and completeness. Operator norm has no such Pythagorean law.
- No-cancellation isolates posterior covariance-error blocks, not all primitive
  model defects. Different models can have identical posterior kernels.
- Explicit versions are available at every observation. Canonical kernels are
  compared with separate evidence-a.e. quantifiers, not an assumed common null set.
- No full Itô derivation, sequential filtering closure, singular-innovation
  pseudoinverse theorem, nonlinear/non-Gaussian result, or refinement optimality.
- No literature priority follows from successful Lean compilation.

## Build discipline

Use the active release's `MODULE_ORDER.json` and `verify_blocks.py`. Compile one
module per outer tool call, with `-j1 -DwarningAsError=true`, in the pinned
Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 environment.
The source manifest and per-process receipts record hashes and dependency hashes.
The original monolithic perturbation file is preserved under PREDECESSOR but the
active build uses nine exact proof-body slice modules. Never import both formats
in one Lean environment: that would duplicate declarations.

Use small resumable groups on a normal local terminal and single modules in
short-lived tool calls. Preserve failed snapshots and timeout receipts. Promote
only actually compiled final sources with clean axiom audits. Do not label the
entire historical chain rebuilt merely because this active layer passes.

## Historical preservation

The exact dated v3 archive is under PRIOR_CHECKPOINTS. Its root controls are copied
to HISTORY/v3_root_control. All inherited CHECKED_RELEASES files are preserved
byte for byte. Earlier historical handoffs retain their original, now outdated
next-task statements; this root document controls continuation.
