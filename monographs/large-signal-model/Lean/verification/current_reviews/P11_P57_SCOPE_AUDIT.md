# P11 and P57 formalization scope

Base checkpoint: Library `Komorebi_Large_Signal_Model_Lean_0.14.0.zip`, frozen source `FOUNDATIONS_1.0.0.md`. Sources edited only by this worker: new `KomorebiLSM/StatisticalRefinement.lean`, `KomorebiLSM/AveragedCongruence.lean`, and their two named negative controls. Shared metadata was not edited.

## P11

Verdict after self-review: proved as written, with a stronger complete real Hilbert-space / finite-measure scope. The original probability-measure and finite-dimensional Hilbert cases are included.

Endpoint: `Komorebi.LSM.StatisticalRefinement.ideal_statistical_benefit_of_integrable_sq_norm`.

Inputs are an ambient measurable space, nested information sigma algebras F ≤ G ≤ ambient, an actual Hilbert-valued random variable Y that is almost everywhere strongly measurable, and integrable squared norm. Both predictors are actual conditional expectations. No residual-orthogonality hypothesis is supplied. `residual_orthogonal` derives it from Mathlib's `condExpL2` projection. `conditional_expectation_pythagoras` proves the L2 risk identity. Representative adapters prove the ordinary Bochner-integral expression using the actual conditional expectations. `ideal_statistical_risk_mono` gives the weak risk inequality.

The negative control `StatisticalRefinementStrictZero.lean` strengthens weak improvement to strict improvement for the zero random variable. After simplifying actual conditional expectations of zero, Lean rejects the remaining goal `False`.

No claim is made about finite-data estimated predictors, changes in distributions, regularization, or strict improvement.

## P57

Verdict after self-review: proved as written for finite real matrices, including every clause in the original proposition. The covariance identity itself does not require symmetric X; positivity uses positive semidefinite X.

Endpoints:

- `Komorebi.LSM.AveragedCongruence.averaged_congruence`
- `Komorebi.LSM.AveragedCongruence.covariance_correction_posSemidef`
- `Komorebi.LSM.AveragedCongruence.affine_covariance_correction`
- `Komorebi.LSM.AveragedCongruence.uniformInterval_variance`
- `Komorebi.LSM.AveragedCongruence.uniformInterval_affine_correction`

`matrixMean` defines matrix integration entry by entry, the canonical finite-dimensional matrix integral. Every matrix entry is assumed L2. The scalar `product_covariance` proof derives the exact covariance expansion after establishing integrability of products. Finite sums transfer it to the matrix identity. Matrix PSD preservation is proved from its Hermitian entries and integrated nonnegative quadratic forms. Affine centering is proved from the actual mean. The normalized Lebesgue measure on Ioc(a,b) is defined and proved a probability measure when a<b. Its actual mean is the midpoint, the identity random variable is proved L2, and its centered second moment is computed exactly as (b-a)^2/12 by polynomial integration. The integrated affine specialization uses this derived coefficient.

After within-team review, the module adds an explicit Bochner-integral dictionary. `matrix_integrable_of_entries` derives actual matrix integrability from integrability of its entries, and `matrixMean_eq_integral` identifies the entrywise integral with the Bochner integral using two finite-coordinate evaluation identities. `matrix_integrable_of_memLp_entries` derives the integrability requirement from the stated L2-entry hypothesis. `averaged_congruence_integral` and `covariance_integral_posSemidef` state the two principal results directly with Bochner matrix integrals. The bridge uses the standard product topology and elementwise matrix norm. Its local elaborator-transparency option resolves reducibility of the matrix type and its topology; kernel checking is unchanged.

The interval width is positive. A zero-width interval does not define a normalized Lebesgue uniform probability measure; no such degenerate law is assumed. The use of Ioc rather than a closed interval changes no Lebesgue-uniform law.

The negative control `AveragedCongruenceZeroCorrection.lean` discards the covariance term for the actual scalar affine family K(u)=u under the uniform unit-interval measure. The exact correction is 1/12, and Lean rejects the resulting goal `False`.

## Verification performed by this worker

Matching portable Lean runtime 4.34.0-rc2, `lean -j1 -DwarningAsError=true`, both positive modules compiled successfully into the private test tree `tmp/l2/KomorebiLSM`. Both controls failed only at the intended semantic contradiction. There are no prohibited source tokens such as proof placeholders or added axioms. Root is responsible for integrating the modules into the cumulative clean build, declaration/axiom audit, kernel replay, and delivery receipts.

Initial compiler failures were implementation diagnostics: instance inference for matrix topology, explicit types for zero conditional-expectation controls, integral rewrite lambda shapes, API spellings, and one style linter. Matrix integration was expressed directly in coordinates rather than depending on a competing matrix-norm topology instance. No mathematical hypothesis was weakened to fix a diagnostic.

Self-review is not independent external review. Root requested separate within-team review before changing coverage.
