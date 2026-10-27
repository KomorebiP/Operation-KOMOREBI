# Finite-Dimensional Joint Covariance Matching v0.1.0 — CHECKED

## Runtime

- Lean: 4.34.0-rc2
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- verification mode: `-DwarningAsError=true`

## Closed in this checkpoint

For finite index types `ι` (state) and `κ` (observation), observation matrix `H`, prior covariance `P`, and noise covariance `R`, under

- `P.PosSemidef`
- `R.PosDef`

with

- `S = H P Hᵀ + R`
- `K = P Hᵀ S⁻¹`
- `Ppost = P - K H P`

Lean checks:

1. `S.PosDef`.
2. exact left/right nonsingular-inverse identities for `S`.
3. `K S = P Hᵀ`.
4. `S Kᵀ = H P`.
5. `K S Kᵀ = K H P`.
6. four joint covariance quadrants:
   - `YY = S`,
   - `XY = P Hᵀ`,
   - `YX = H P`,
   - `XX = K S Kᵀ + Ppost = P`.
7. exact packed block equality `reverseJointCov = forwardJointCov`.
8. exact Joseph covariance = Schur covariance `Ppost`.
9. `Ppost.PosSemidef` derived from the Joseph representation; it is not assumed.
10. `forwardJointCov.PosSemidef` via the Schur-complement theorem.
11. `reverseJointCov.PosSemidef` by exact covariance equality.

## Verification receipt

A clean sequential rebuild was performed after deleting the six cached project `.olean` files:

- `FDKalmanDefs`: RC=0, 8.61 s
- `FDInnovationIdentities`: RC=0, 8.69 s
- `FDJointCovQuadrants`: RC=0, 9.15 s
- `FDJointCovAssembly`: RC=0, 9.40 s
- `FDPosteriorCovPSD`: RC=0, 9.85 s
- `FDJointCovPSD`: RC=0, 9.57 s

Representative axiom audits use only:

- `propext`
- `Classical.choice`
- `Quot.sound`

Placeholder scan:

- `sorry`: 0
- `admit`: 0
- custom `axiom`: 0

## Explicit OPEN boundary

The measure-level theorem equating the actual forward prior/likelihood `compProd` joint law with the reverse evidence/posterior `compProd` joint law is **not yet promoted here**.

`open_not_checked/FDGaussianJointParamEquality.lean` is a one-rewrite probability-facing wrapper around the checked covariance equality, but loading the full Mathlib multivariate-Gaussian module exceeded the execution window before diagnostics. It is therefore preserved as OPEN / NOT CHECKED.

The next durable block is to rebuild the previously developed small Gaussian-transport / affine-kernel modules against this normalized covariance core, then prove the actual forward/reverse joint-measure equality and invoke disintegration uniqueness.
