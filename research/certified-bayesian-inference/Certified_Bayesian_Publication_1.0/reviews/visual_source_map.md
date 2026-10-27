# Extended visual guide: source and scope map

Author: Komorebi P. Publication edition 1.0.

Manuscript: `manuscripts/visual.tex`. Scope: 35 paced sections, 20 exact mathematical figures, one-observation Gaussian inference, exact cached selective updates, independent outward-rounded final verification, and parameter intervals for the returned gain's Joseph Gaussian.

## Section map

All Lean filenames below refer to `source/FD_Certified_Inference_Core_v1.0.0_Checked/Komorebi/` unless another relative path is shown.

| Section | Principal evidence | Interpretation limit |
|---|---|---|
| 1 Contract | RELEASE_SCOPE.md; CachedPacketOutput.lean; PosteriorOutputSemantics.lean | One fixed finite-dimensional observation model, positive rational tolerances, fixed complete packets. |
| 2 Observation | RationalCertificateChecker.lean; FDInnovationConditioning.lean | Exact observed data. No uncertainty-in-input or sequential contract. |
| 3 Exact posterior | FDPosteriorKernel.lean; FDGaussianConditioning.lean; FDInnovationConditioning.lean | Explicit posterior version at each y; equality to canonical conditional law evidence-almost everywhere. |
| 4 Singular prior | examples/adaptive_rotated.json; FDPosteriorCovPSD.lean | Invertible innovation does not require invertible prior. Displayed line segments illustrate scale within unbounded support. |
| 5 Joseph approximation | FDInexactGainAlgebra.lean; FDGainSampler.lean | Arbitrary gain defines a valid Gaussian; not exact conditioning unless exact gain. |
| 6 Residual-to-law bound | FDInexactGainCoupling.lean; FDResidualEnergyCertificate.lean | Inverse-free residual majorant is a sufficient squared-Wasserstein bound, not equality with W2. |
| 7 Packets | RationalPacketCertificates.lean; AdaptivePacketInvariants.lean | Fixed, complete, self-adjoint, mutually orthogonal rational families. Input/output roles differ. |
| 8 Energy ledger | PacketSelectiveAlgebra.lean; CachedPacketState.lean | Exact squared-energy addition; no roundoff cancellation claim. |
| 9 Coordinate fixture | examples/adaptive_coordinate.json; results/cached_coordinate.json; GeneratedCachedCoordinate.lean | Exact fixture data and output; archived timing belongs to a particular run. |
| 10 Six updates | CachedPacketTrajectory.lean; GeneratedCachedCoordinate.lean | Actual selected packets and rational iterates; alternation is fixture-specific. |
| 11 Final coordinate law | FDInexactGainAlgebra.lean; reviews/exact_example_results.json | Joseph covariance excess derived exactly; not the Wasserstein distance. |
| 12 Cache state | CachedPacketState.lean: initialState_valid, step_valid, score_eq | Prepared model constants and actual initialization, not arbitrary user-supplied valid-cache claims. |
| 13 Preservation | AdaptivePacketInvariants.lean; CachedPacketState.lean | Orthogonality kills unselected cross terms; fixed model/packets required. |
| 14 Selection | GreedyPacketSelection.lean; CachedPacketTrajectory.lean | Covering scan, seed nonemptiness, strict replacement, incumbent tie retention. |
| 15 Rate | GreedyPacketConvergence.lean; CachedPacketTrajectory.lean | Uniform mathematical envelope; not timing or bit complexity. |
| 16 Fuel | CachedPacketSearch.lean; AdaptivePacketSolver.lean | Sufficient finite fuel, last state tested, actual return origin. Not hardware success under caps. |
| 17 Slack | CachedPacketSearch.lean; CachedPacketSolver.lean; PrecisionCompleteness.lean | Search threshold epsilon²/4 and final epsilon² distinct. |
| 18 Final evaluation | RoundedCandidate.lean; RoundedPosteriorSound.lean | Canonical operations: checkSetup, roundedCandidate, checkTolerance. checkCandidate=true is established by soundness, not separately executed there. |
| 19 Precision | TaggedPrecisionSearch.lean; PrecisionCompleteness.lean; both cached result JSONs | Probe 4 fails; probe 12 passes. Fallback 72 sufficient in both fixtures, not required actual precision. No universal strict monotonicity. |
| 20 Dyadic balls | DyadicBall.lean; DyadicPrecision.lean; RationalBall.lean | Explicit center/radius fixed-point model; not IEEE hardware semantics. |
| 21 Outputs | PosteriorOutput.lean; PosteriorOutputPrecision.lean; PosteriorOutputSemantics.lean | Entrywise enclosures of approximation parameters at returned gain. Display translated/rescaled by 2^32. |
| 22 Epsilon/delta | RELEASE_SCOPE.md; PosteriorOutputSemantics.lean | Delta not exact-posterior parameter error. Centers not a separately certified Gaussian. |
| 23 Rotated fixture | examples/adaptive_rotated.json; GeneratedCachedRotated.lean | Singular support, observation direction, and residual packet distinct. |
| 24 Four updates | results/cached_rotated.json; FDInexactGainAlgebra.lean; fresh exact results | Gain all203/625; Joseph covariance all130379/390625; exact posterior all1/3. Excess coefficient 512/1171875. |
| 25 Naive cache failure | CachedRoundingBoundary.lean | Scalar checked counterexample to independent center-only gain/residual rounding. No general rounded-cache impossibility. |
| 26 Rejection | CachedRoundingBoundary.lean; CachedPacketSolver.lean | Sound final verifier rejects; invalid optimization loses promised success/termination proof. |
| 27 Arithmetic boundary | README.md; DyadicBall.lean; fresh exact results | Fresh covariance-center counterexample is exact Python/rational diagnostic, not new Lean theorem. No parser/hardware/sampler refinement. |
| 28 Branches | RoundedSolverSearch.lean; AdaptivePacketSolver.lean; CachedPacketSolver.lean | Exact cached, recomputed selective benchmark, and rounded full-gain branches distinct. |
| 29 Instance evidence | GeneratedCachedCoordinate.lean; GeneratedCachedRotated.lean; results/FORMAL_INSTANCES.json | Two full program/output examples versus 21 static final-candidate benchmark certificates. |
| 30 Caps and parser | README.md; checks/cached_posterior.py; CachedPacketOutput.lean | Mathematical finite success versus practical resource limits; serialization refinement not proved. |
| 31 Benchmark | BENCHMARK_REPORT.md; results/FULL_COST_BENCHMARK.json; computations/release-final/benchmark/benchmark.json | Archived producer medians; costs not scalability/BLAS/GPU superiority. Full-cost estimate not end-to-end sampled distribution. |
| 32 Verification | FINAL_VERIFICATION_RECEIPT.json; VERIFICATION_SUMMARY.md; MODULE_ORDER.json | Archived build117 modules / axiom audit543 declarations. Fresh source/Python diagnostics do not rerun kernel. |
| 33 Assurance | SELF_REVIEW.md; RELEASE_SCOPE.md; CachedPacketOutput.lean | Completed integrated scoped artifact, no broad novelty/priority inference. |
| 34 Extensions | RELEASE_SCOPE.md; ROUTE_RECORD.md; FAILURE_LOG.md | Concrete missing obligations stated; no claim those extensions are completed. |
| 35 Reading back | PROOF_NOTE.md; CachedPacketOutput.lean; both generated examples | Complete reading route through the declared scope. |

## Figure integration

All 20 figure stems in `reviews/figure_catalogue.json` occur exactly once in the guide. They are reproduced from the producer's PDF files, with `height=0.36\textheight` and `keepaspectratio`. Captions are guide-specific prose aligned to the exact producer data and scope. No AI bitmap imagery is used.

Special figure scope labels retained:

- Gaussian contours are numerical renderings of exact matrices, with one-standard-deviation level sets rather than confidence regions. The observation line is not a state-support constraint.
- Singular line segments illustrate two latent standard deviations, rather than finite mathematical support.
- Log plots use numerical display coordinates for exact rational values.
- The covariance excess is an algebraic identity, not W2.
- Output intervals are translated relative to exact Joseph parameters and rescaled by 2^32, never identified as exact-posterior entrywise error.
- Precision curve shape is fixture-specific.
- Benchmark numbers are archived release-final producer measurements, not fresh speed tests.

## Bounded mathematical proofreading self-review

Reviewed the entire authored manuscript and nearby local source definitions needed to settle notation, source routes, and interpretation.

- Routine edits: source filename corrections; benchmark provenance correction; figure-specific caption alignment; explicit final-evaluator operational description.
- Mathematical-token corrections: two initial superscript transcription errors `^{,2}` corrected to `^{2}` in the Frobenius/packet energy displays. Independently audited rotated Joseph excess decomposition corrected from `1/3 + 256/1171875` to `1/3 + 512/1171875`; the primary coefficient `130379/390625` and all gain/score values were already correct. This substantive derived-identity repair follows the independent raw model derivation, not proofreading inference alone.
- Structural checks: 35 section headings; 20 unique figure references; no unresolved referenced Lean source filenames; balanced document/figure/pmatrix environments. Figure assets present.
- Unresolved mathematical issues from this author's self-review: none. Independent audit and root PDF rendering are recorded separately.
- Validation: no fresh Lean compilation by this guide author. Root handles LaTeX compilation and rendered page QA.
