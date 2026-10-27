# Komorebi Unified Inference / Stochastic / Bayesian — continuation checkpoint v2

**Checkpoint:** 2026-09-09, America/Chicago

This capsule supersedes the prior `Komorebi_Unified_Inference_Stochastic_Bayesian_CONTINUATION_2026-09-09.zip` handoff for this branch. The prior handoff was restored and its full SHA-256 manifest verified before continuation.

## 1. Pinned verification environment

Every theorem promoted here as `Checked` was compiled in the preserved portable environment:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- `-DwarningAsError=true`
- checked sources have zero `sorry`, `admit`, or custom axioms
- representative axiom audits reduce to `propext`, `Classical.choice`, and `Quot.sound`

The large runtime itself is not duplicated in this ZIP. `LEAN_RUNTIME_METADATA/` preserves the exact reconstruction metadata and hashes for `Lean_Compact_01.zip` through `Lean_Compact_05.zip`.

## 2. Restored CLOSED chain

All CLOSED blocks from the previous handoff remain CLOSED and were not re-proved merely for duplication. They include:

- Unified Inference Lean v0.1 through v0.6;
- stochastic covariance residual theorem;
- coordinate/dyadic stochastic polyphase refinement;
- abstract orthogonal-projector stochastic refinement;
- finite-time multiscale covariance stability;
- time-varying multiscale Duhamel refinement;
- Bayesian multiscale Kalman posterior perturbation;
- scalar identity-observation Gaussian/Kalman semantic conditioning v0.1.0.

The previous full handoff manifest passed `sha256sum -c` with exit code 0. See `AUDIT_TRAIL/ORIGINAL_HANDOFF_MANIFEST_CHECK.log`.

## 3. NEW CLOSED block A — arbitrary scalar observation coefficient

Release:

`CHECKED_RELEASES/Gaussian_Kalman_Bayesian_Conditioning_v0.2.0_Checked`

Model:

`X ~ N(m,p)`, `p>0`

`Y | X=x ~ N(hx,r)`, `r>0`, arbitrary `h : ℝ` including `h=0`.

Definitions:

`S = h^2 p + r`

`K = p h / S`

`m+(y) = m + K (y - h m)`

`p+ = p r / S`.

Lean now checks the generalized completing-square identity, normalization constant identity, real and ENNReal Gaussian density factorization, exact evidence marginal `N(hm,S)`, prior/likelihood and evidence/posterior joint-density representations, exact disintegration identity, evidence-a.e. equality with Mathlib's canonical posterior, pointwise normalized Bayes density equality, and normalized Bayes measure equality for every fixed observation.

Central source SHA-256:

`61ea8047e9e2ccf310d70696263c888ac50150f3c012df7d4db2f5a49fa6a6ac`.

Final warning-as-error source recheck: exit 0. Fresh representative axiom audit: exit 0.

## 4. NEW CLOSED block B — scalar semantic integration with perturbation theory

Release:

`CHECKED_RELEASES/Scalar_Gaussian_Posterior_Perturbation_Semantic_Bridge_v0.1.0_Checked`

This closes the semantic gap in the already checked coordinate-free Kalman perturbation theorem for the scalar linear-Gaussian model.

Lean checks, among other statements:

- the scalar realization of `H`, `P`, `R`, innovation, inverse innovation, Kalman gain, posterior mean, and Joseph posterior covariance;
- `posteriorCovErrorOp` is exactly multiplication by the difference of the actual Gaussian posterior variances;
- the checked end-to-end posterior-mean residual budget applies directly to the difference of actual Gaussian conditional-posterior means;
- the checked posterior-covariance residual budget applies directly to the difference of actual Gaussian conditional-posterior variances;
- the coordinate-free scalar update is the explicit Gaussian posterior, equals a Mathlib canonical posterior version evidence-a.e., and equals the normalized Bayes measure for every fixed observation.

Central source SHA-256:

`9626910363c06e325d38898ee8d7f112cdf3f38eda3d2cb3eedcbc249c1b0915`.

Final warning-as-error bridge recheck against the exact compiled dependency snapshots: exit 0. The preserved completed bridge axiom audit reports only `propext`, `Classical.choice`, `Quot.sound` for the audited load-bearing theorems.

## 5. What is now semantically proved

For scalar linear-Gaussian observations, the perturbation variables `m+` and `P+` are no longer merely algebraic Kalman updates. They are parameters of an actual Bayesian conditional-posterior version. Therefore the checked scalar perturbation bounds are genuine bounds on parameters of actual conditional posteriors.

This does **not** make one-dimensional state space a nontrivial multiscale spatial decomposition. The multiscale projector/refinement theory only acquires nontrivial posterior semantics once a finite-dimensional or Hilbert-space Gaussian semantic bridge is supplied.

## 6. Strongest next OPEN theorem

Proceed next to **finite-dimensional nonsingular Gaussian conditioning**.

Target model:

`X ~ N(m,P)`

`Y = H X + ε`, `ε ~ N(0,R)` independent,

with positive-definite/nonsingular covariance hypotheses sufficient to justify densities and inverses.

Target formulas:

`S = H P H* + R`

`K = P H* S^-1`

`m+(y) = m + K (y - H m)`

posterior covariance `P+ = (I-KH)P`, preferably also proved equal to the Joseph form under the relevant hypotheses.

Required semantic closure:

1. construct or reuse a finite-dimensional multivariate Gaussian density theorem with explicit normalization;
2. prove the joint density factorization/completing-square identity;
3. prove the evidence marginal;
4. construct the explicit posterior kernel;
5. prove normalized Bayes equality and canonical-posterior equality via disintegration;
6. only then combine it with `Bayesian_Multiscale_Kalman_Posterior_Perturbation_v0.1.0_Checked` to obtain a genuinely multiscale theorem about actual posterior kernels.

## 7. Explicit proof boundaries

**OPEN / NOT CLAIMED:**

- arbitrary finite-dimensional observation operator `H` with multivariate Gaussian semantic conditioning;
- singular/degenerate multivariate covariance treatment;
- a nontrivial multiscale posterior-kernel theorem;
- Wasserstein, Hellinger, or KL posterior stability driven by the residual budget;
- literature priority or novelty.

Do not promote any of those statements merely from the scalar result.

## 8. Recorded execution failures

No mathematical counterexample was found in the completed blocks.

Execution issues that occurred and must not be hidden:

1. An initial path lookup assumed `CONTINUE_HERE.md` was directly under an extraction directory; the ZIP actually had a top-level folder. This was corrected by reading the nested file.
2. A bundled full rebuild of both dependency modules plus the scalar bridge exceeded the 240-second tool execution window. It is not counted as verification evidence. The exact dependencies were separately compiled in the pinned runtime and the bridge then compiled against those artifacts with exit code 0.
3. A later redundant combined axiom-audit retry completed the general-scalar audit but timed out during the bridge audit before output. It is not counted as bridge axiom evidence. The earlier completed bridge axiom audit remains the evidence record.

These are environment/tool-timeout failures, not Lean theorem failures.

## 9. Continue protocol

Do not re-prove CLOSED blocks. Start from finite-dimensional Gaussian conditioning. Preserve exact covariance/invertibility hypotheses, run warning-as-error Lean checks, scan for placeholders/custom axioms, perform representative `#print axioms` audits, and record source/output hashes before promoting anything to `Checked`.
