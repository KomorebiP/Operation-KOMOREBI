# Paper VIII sixth-block actual results

**Author: Komorebi P.**

Theorem 5.6 is checked under the explicit factorization hypotheses of the manuscript. The 56-item manuscript-proved register is complete within those scopes. Four classical inputs are separately tracked.

## Counts

| Measure | Fifth block | Sixth block |
|---|---:|---:|
| Covered manuscript-proved items | 55/56 | 56/56 |
| Active proof modules | 30 | 40 |
| Named theorem declarations | 313 | 392 |
| Separately audited constructions | 36 | 66 |

The 79 added declarations include supporting lemmas. The cumulative 392 include 19 unchanged reused quantum-packet theorems and 373 Paper VIII declarations. They are not 392 independent discoveries.

## Mathematical work

Actual input column spaces give compact orthonormal factors with dimensions equal to matrix ranks, including zero/rank-deficient factors. Given ordered thin SVD equations for the actual core, the construction returns factors with exactly min(d,k) columns. The product has rank at most k, is globally optimal in spectral and Frobenius norm against all ambient rank-bounded competitors, and has exact next-value and Frobenius tail errors.

The proof does not assume best approximation. Spectral optimality uses a nonzero kernel witness supported in the first k+1 coordinates. Frobenius optimality uses the actual kernel frame, row weights between zero and one, rank-nullity and a proved finite weighted-tail inequality. Norm/rank preservation under isometric lifting and contractivity under compression are proved, then used to transfer optimality to arbitrary ambient competitors. Thin square-root factors and zero/full-retention endpoints are checked.

General SVD existence, an algorithm for computing an SVD or QR, and identification with the canonical Mathlib singularValues API are not independently formalized. The exact SVD reconstruction, nonnegative ordering and orthonormality equations are supplied, as in the manuscript's 'take an SVD' hypothesis. No norm invariance, tail-error or optimality conclusion appears in that certificate.

## Fresh checks

All 40 modules compiled in a new output directory, with warnings fatal. All 392 theorem and 66 construction dependency audits matched the inventory and used only propext, Classical.choice and Quot.sound, or subsets. Both invalid-proof controls were rejected. Mathlib's supplied pinned compiled cache was reused, not rebuilt.

Forty-three current unit tests passed: 17 verifier, 12 updated fifth-block compatibility and 14 sixth-block tests. The original fixed-count fifth-block test file is preserved. The independent complex128 mirror passed 638 truncation cases over 182 factor pairs, 3,190 arbitrary competitors, nine input-rejection controls and two mathematical assumption-removal controls. These finite tests are not additional universal theorems or executions of Lean definitions.

The eight-page supplement compiled without final TeX warnings or over/underfull boxes. Every page was rendered and visually inspected. The original manuscript, its bibliography/source package, all 30 upstream proof files and all five earlier PDF/TeX supplements remain byte-identical.

## Failed development attempts

Twenty-one of 31 captured development checks failed before correction. Inactive snapshots and diagnostics remain in verification/development_sixth. The accepted clean cumulative run is separate and complete. An initial interactive runtime recovery launch was unsupported. Noninteractive assembly succeeded after that, with all seven part hashes and the combined archive hash verified.

## Boundaries and next document step

The original performance corpus, CPU/GPU benchmarks, earlier compiler execution suites and Papers I–VII in full were not rerun. No imported Mathlib proof corpus was independently rechecked. The formalization does not establish a new dense-matrix exponent, CUDA kernel verification or floating-point stability theorem.

The full original manuscript is preserved rather than rewritten. Integrating the cumulative amendments and final recompression proof into a primary reading copy, then proofreading it, is the next document step. The exact source-to-statement correspondence is a mathematical review, not an automatically verified semantic equivalence.
