# Claim boundaries

## Proved finite statements in the manuscript

The finalized manuscript proves the following statements for the declared finite model:

- Fixed-support, fixed-unfolding, fixed-rank truncated SVD optimality in Frobenius norm
- Exact integer-budget dynamic programming for the declared additive tree model
- Budget monotonicity of the finite frontier
- Least-squares dominance of global refitting within a completed span
- Exact residual energy gain after orthogonal block projection
- Finite portfolio nonregression because unchanged seeds remain available
- Singular subspace stability under a positive retained-discarded gap and bounded perturbation
- Exact residual-archive reconstruction
- Complete finite-raster closure through singleton pixel-channel packets

## Computed finite results

The repository preserves the following computed evidence:

- Four-image final portfolio benchmark
- Exact tree frontier sizes and timings
- Ten structural stress cases
- Thirty-six noise scenarios
- 12,154 implementation-verification scenarios
- 9,960 exact dynamic-programming comparisons against exhaustive enumeration
- Eighty-five vector figures used in the finalized manuscript, with additional development assets preserved in the archival snapshot

These results are attached to the declared images, dimensions, budgets, packet grammar, parameter proxy, and implementation version.

## Model-dependent components

The following choices remain heuristic or application dependent:

- Moving residual region proposals outside the fixed tree
- The order in which seed directions are reopened
- The scalar parameter-cost proxy
- The packet grammar available to the search
- The default complexity exponents
- Noise behavior without a statistical noise model
- Extrapolation beyond tested dimensions, budgets, and image families

## Statements not made

The repository does not assert that:

- Global SVD is inferior in its own fixed-rank approximation class
- Every image admits a short semantic packet description
- The parameter proxy equals a compressed bit count
- AM-SPD is an automatic denoiser
- Exact residual accounting is equivalent to sparse exactness
- The reported benchmark values generalize universally


## Software-format boundaries

The `.amspd` archive is a reproducibility and interchange format. It is not an entropy-coded compression standard. A model with `residual_storage=none` preserves only the approximation. A sparse model with a positive residual threshold is deliberately lossy and is not labeled as exact closure. SHA-256 payload checks detect modification but do not establish authorship or authenticity.

Residual closure applies to the normalized floating-point raster after input conversion. Subtraction and addition can introduce roundoff. It does not imply bit-for-bit floating-point recovery, original image-file recovery, or retention of container metadata and arbitrary scientific intensity scales. Ordinary image export may add quantization or lossy compression; use `.npy` for normalized floating-point output.

## Version 1.0.0 execution boundaries

- Exact continuation means floating-point parity with the uninterrupted packet search only when the schema-2 frontier, source image, active atoms, and search-affecting configuration are unchanged.
- `frontier-exact` retains the original finite candidate frontier but reconstructs the source through residual closure. Roundoff can affect source coordinates and subsequent search decisions, so uninterrupted parity is not guaranteed on this path.
- Schema-1 continuation is a deterministic warm start. It is not represented as the original historical frontier.
- Tiled execution optimizes independent local problems and blends their outputs. It is not equivalent to one globally coupled AM-SPD optimization.
- Automatic selection minimizes only over the declared finite configuration grid and chosen proxy objective.
- Batch run fingerprints establish configuration identity for result reuse. They are not cryptographic attestations of the executing environment.
- Multiworker execution does not turn the implementation into a streaming or GPU algorithm.
