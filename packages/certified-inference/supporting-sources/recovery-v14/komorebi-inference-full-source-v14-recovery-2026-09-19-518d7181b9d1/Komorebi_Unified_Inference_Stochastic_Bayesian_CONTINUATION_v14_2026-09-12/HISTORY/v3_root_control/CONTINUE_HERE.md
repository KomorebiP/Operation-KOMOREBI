# Continue the Unified Inference / Stochastic / Bayesian program

## Restored state

The complete v2 checked chain is preserved under `CHECKED_RELEASES/`. Its scalar
Y=hX+epsilon conditioning and scalar perturbation semantic bridge remain the
previous recorded checked results. Consult `HISTORY/v2_root_control/CONTINUE_HERE.md`
for the full earlier research synthesis and boundaries, not for the next task.

## New completed theorem

Open `CHECKED_RELEASES/FD_Gaussian_Bayesian_Conditioning_v0.1.0_Checked/Komorebi/FDGaussianConditioning.lean`.

For arbitrary finite real index types, P positive semidefinite, R positive
definite, and rectangular H, the actual Gaussian likelihood/prior joint equals
the evidence/explicit-Kalman-posterior joint. Therefore the actual evidence is
N(Hm,HPHᵀ+R), and Mathlib's canonical Bayesian posterior is evidence-a.e.

    N(m + K(y-Hm), P-KHP),    K = PHᵀ(HPHᵀ+R)⁻¹.

The covariance also equals the Joseph expression. Its positive semidefiniteness
is derived. P is allowed to be singular. No inverse of P, conditional-law
identity as an assumption, or custom axiom is used.

The 18-module layer contains 51 theorem/lemma declarations, 17 retained and 34
newly checked. All modules were rebuilt from final project sources with warnings
as errors; all 51 declarations passed the axiom audit. Pinned mathlib compiled
dependencies were reused. This is not a fresh full rebuild of all prior releases.

## Strongest next theorem

Complete the finite-dimensional multiscale posterior perturbation semantic bridge.
Work from the new release's `CONTINUE_HERE.md` and

    CHECKED_RELEASES/Bayesian_Multiscale_Kalman_Posterior_Perturbation_v0.1.0_Checked/src/BayesianMultiscaleKalmanPosteriorPerturbation.lean

Prove matrixCLM compatibility with matrix products and continuous-linear-map
composition. Transpose/adjoint compatibility is already checked. Derive the
innovation inverse map equations from the checked two-sided matrix identities.
Identify matrix gain and Joseph posterior covariance with the earlier operator
definitions, then identify their covariance error operator with the actual
Gaussian posterior covariance discrepancy.

Attach the existing norm budgets and orthogonal-descendant refinement only after
these identifications compile. Keep operator norms distinct from Frobenius or
Hilbert-Schmidt norms. Preserve the nontrivial error D=P-P0 rather than assuming
the true covariance has the reference model's exact packet closure.

When comparing two models, use the explicit posterior versions for a statement
at arbitrary observations. Each equality to a canonical version is with respect
to that model's own evidence measure. A common-null-set or cross-measure claim
needs its own absolute-continuity or null-set-transfer proof.

## Explicit remaining boundaries

The nontrivial finite-dimensional multiscale semantic integration, posterior
metric bounds, singular innovation/pseudoinverse cases, Itô derivation, and
nonlinear/non-Gaussian extensions remain open. No multivariate normalized-density
formula for every observation is claimed. No literature novelty is established.

## Verification and execution

Read `PROTOCOL.md` and `CHECKED_RELEASES/FD_Gaussian_Bayesian_Conditioning_v0.1.0_Checked/FINAL_VERIFICATION_RECEIPT.json`.
Use the exact pinned Lean 4.34.0-rc2 / mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
runtime. Run separate small Lean invocations, not a single monolithic compilation.
The new release's reproduction runner records each process independently and
rejects a different runtime. The incomplete paired-call timeout is documented
and not counted as evidence. All final modules subsequently passed individually.

Do not relabel anything checked without a successful final compile and appropriate
axiom audit. Preserve exact source hashes, failed attempts, hypotheses, and the
remaining proof boundaries. Numerical covariance checks are not substitutes for
the joint-measure proof or for future universal perturbation theorems.
