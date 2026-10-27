# Komorebi Unified Inference / Stochastic / Bayesian — v5

Checkpoint: 2026-09-11 (America/Chicago).

## Restored state

The scalar Gaussian, finite-dimensional Gaussian-conditioning, and finite-dimensional
multiscale posterior-moment bridge releases remain preserved. The v5 addition is

    CHECKED_RELEASES/FD_Posterior_Coupling_v0.1.0_Checked

Read its PROOF_NOTE.md, CONTINUE_HERE.md, FINAL_VERIFICATION_RECEIPT.json and the
main Lean sources. The active slice has 31 compiled modules and 119 audited theorem/
lemma declarations: 53 retained dependency declarations and 66 new declarations.
These are declaration counts, not counts of independent mathematical discoveries.

## Newly CLOSED_CHECKED

1. Actual shared-Gaussian-source coupling, its two probability marginals, and exact
   quadratic cost. Gaussian second moments and integrability are proved.
2. A standard ENNReal all-plan squared W2 infimum, its root convention, probability
   plan normalization, and shared-source upper bound. Full metric axioms and optimal
   plans are not part of this release.
3. Inexact-gain Bayesian posterior approximation. With S=HPHᵀ+R, v=y-Hm,
   F=PHᵀ-BS, and J(B)=(I-BH)P(I-BH)ᵀ+BRBᵀ:

       W2²(eta_y,N(m+Bv,J(B))) <= ||F S⁻¹ v||²+tr(F S⁻¹ Fᵀ).

   The exact Joseph covariance excess is F S⁻¹ Fᵀ >= 0. It is derived.
4. If R >= sigma I, sigma>0, the actual S inverse norm is <= 1/sigma. Consequently

       W2² <= ||F||F² (1/sigma+||v||²/sigma²).

   The squared stopping condition ||F||F²(sigma+||v||²)<=epsilon² sigma²,
   epsilon>=0, implies W2<=epsilon. The reported majorant needs no exact gain,
   posterior covariance or innovation inverse. It is not verified floating point.
5. Full two-model posterior-factor comparison, with P=LLᵀ, R=NNᵀ and compatible
   latent dimensions:

       W2²(eta_y,eta0_y0) <= ||a-a0||²
           + ||(I-KH)L-(I-K0H0)L0||F² + ||KN-K0N0||F².

   Actual posterior sampler laws are proved. The chosen coupling need not be optimal.

## Strongest next open theorem

Prove a finite self-adjoint orthogonal-projector Hilbert-Schmidt/Frobenius energy
refinement theorem for rectangular residuals and factor discrepancies. Require the
appropriate completeness and both source/target inner-product structures explicitly.
Then apply the additive nonnegative energies to the checked residual W2 stopping
certificate. Refining the accounting of a FIXED residual does not itself decrease
the error or prove an adaptive algorithm's progress.

After this, address certified numerical majorants, admissible covariance-preserving
updates and acceptance rules. Factor discrepancies still require comparison with
primitive covariance errors under stated hypotheses. Finite-horizon filtering kernel
recursion remains the later major probability step. The review's sharper four-term
covariance identity is a separate unformalized target and must remain labeled so.

## Proof boundaries to preserve

P may be singular; R must remain positive definite. Canonical versions agree only
under their evidence-a.e. scope; explicit versions are pointwise. An arbitrary gain
produces a valid Gaussian approximation, not the original model's exact posterior.
The gain equation residual is not a floating-point-certified number merely because
its algebra is formalized. Noise floors are mathematical inputs, not a verified
numerical eigenvalue routine. No automatic factor alignment, coupling optimality,
primitive-error identifiability, operator-norm Pythagorean law, adaptive termination,
full sequential filtering, singular-innovation theorem, general Ito derivation,
nonlinear/non-Gaussian extension or literature novelty is asserted.

## Build and evidence

Pinned Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Use the active release's module
order and one Lean process per tool call, -j1 -DwarningAsError=true, 40-second
process cap. The 16 retained dependencies in the new slice were freshly compiled;
the full older v4 and continuous-time chains were not rebuilt this turn. All active
sources, successful and failed snapshots, dependency hashes and complete axiom audit
are retained. Do not import both normalized modules and an old monolith declaring
the same names. Every final theorem/lemma requires a successful pinned check.

Root v5 controls supersede previous next-task statements. All inherited checked
release files remain byte-for-byte unchanged; historical statuses are snapshots.
