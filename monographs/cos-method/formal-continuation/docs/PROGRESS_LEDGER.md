# Progress ledger — K-COS end-to-end branch v0.1.0

## Baseline and immutability

The authoritative predecessor is the official K-COS publication package 1.0.0 from this conversation. Its PDF and ZIP are not edited. The two original mathematical modules, `FiniteGram.lean` and `Certificates.lean`, are copied unchanged. Exact identities and source hashes are in `provenance/BASELINE.json`.

The pinned toolchain is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Nine dependency repositories must match their pins and have clean tracked sources.

## Added formal blocks

- `TailProbability.lean`: actual closed upper-tail events, measurability, finite/probability measure bounds, almost-everywhere invariance and order, threshold monotonicity, weighted-square coupling, endpoint composition, and measurable Gram/energy laws.
- `Acceptance.lean`: multiplicative accuracy, relative-error soundness, an exact rational Boolean checker, tolerance monotonicity, interval narrowing, and the distinction between midpoint and full-interval error budgets.
- `GaussianTail.lean`: concrete standard-Gaussian product measure, coordinate laws, independence, actual spectral pushforward law, stochastic bounds, and conditional acceptance.
- `SpectralGaussian.lean`: orthonormal diagonalization, the actual Gaussian law of a symmetric operator, spectral tail identity, and the operator-to-accuracy composition.
- `CentralLinearImage.lean`: exact reduction for X = BZ to B* M B, including singular B, and its conditional probability-accuracy contract.
- `MatrixGaussian.lean`: the original finite matrix/Gram interface connected to the Euclidean spectral reduction and final conditional acceptance theorem.

## Verification authority

`verification/accepted/run.json` is authoritative only when its status is PASS. `docs/DECLARATIONS.json` gives the exact source inventory. The report distinguishes compiler acceptance, project-only kernel replay, axiom audit, accepted controls, and intended rejection controls. Development failures remain under `verification/development/` and any nonaccepted replay attempts remain separately named.

The accepted checkpoint contains 85 production theorems, 19 definitions, and one named probability-measure instance: 105 explicitly audited declarations. The predecessor had 26 theorems and eight definitions. Generated internal helper declarations are not separately included in these source counts; dependencies of each explicitly audited declaration are checked transitively by Lean's axiom audit.

## Next exact restart point

Create `KomorebiQCOS/TiltedMeasure.lean`, importing the current probability interface. Work from an actual probability measure μ and measurable statistic Q.

1. Define the exponential moment and tilted measure using an actual density, not a supplied probability law. State integrability and strict positivity of the normalizer explicitly.
2. Prove normalization and the change-of-measure identity for the closed upper-tail payoff. Derive the equality from integration against the density, rather than taking the identity as a hypothesis.
3. Specialize to the positive weighted-square Gaussian law after deriving its exponential moment on the admissible domain.
4. Derive the tilted support/Chernoff bound and connect it to the existing tail event. Preserve the distinction between an exact analytic bound and an executable interval enclosure.

A parallel later block can verify numerical spectral inclusion. Do not bypass either route by replacing an unproved conclusion with an instance or an assumption named "certificate".

## What remains open

The full Python implementation, the numerical eigenvalue enclosure constructor, COS inversion and analytic remainders, interval/transcendental-library semantics, parsing, serialization, covariance-input interpretation, and noncentral extension are not verified end to end. The conditional composition theorem exposes these outstanding premises. See `END_TO_END_TARGET.md` and `COVERAGE.json` for the precise scope.
