# Lean companion source map and self-review

Author: Komorebi P. Publication manuscript: `manuscripts/lean.tex`.
Source release: `source/FD_Certified_Inference_Core_v1.0.0_Checked`.

## Delivered content

The companion has 23 explanatory sections and two appendices. It presents the returned contract first, then follows the dependency route through represented Gaussian semantics, actual joint-law disintegration, gain/residual transport bounds, complete packet geometry, exact finite candidate/tolerance checks, selective locality, greedy maximum selection, finite fuel, exact cached-state invariants, trajectory equivalence, bounded search, outward dyadic final verification, and interval-output semantics.

Two complete archived execution instances are explained: a two-state/one-observation coordinate model, and a singular rank-one prior with rotated packets. A formally rejected naive rounded cache and three archived intentionally invalid Lean controls identify concrete failure boundaries. A complete module-order map lists all 117 active modules and the named theorem/lemma count in each. Working-copy rebuild and proof-producing-instance commands preserve the archived evidence rather than overwriting it.

There are **94 exact source-attributed excerpts**, consisting of **47 definitions/structures/abbreviations and 47 complete theorem/lemma proof bodies**. The excerpts retain the exact UTF-8 source, with inclusive file/line locators. Full proof means the entire named declaration and proof body, not a standalone module with all ambient imports/variables repeated. Namespace, finite-type instances, opens, and inherited variables remain in the original module. Listings contain no ellipsis substitutions. The separate intentionally failing dropped-radius control is plainly labeled and not included in the accepted-proof count. Commands are illustrative reproduction instructions and not reported as executed during this session.

`scripts/author_lean_companion.py` reproducibly generates the inline listings and metadata from immutable archived source spans. `scripts/lean_inventory.py` independently reads the resulting manuscript and compares every attributed listing to its exact original line span and digest. The current manuscript should be compiled by the publication build process. Regenerating it discards any direct manual edits, so authoritative companion edits should also update its authoring script.

## Claim-to-source map

| Companion topic | Authoritative project modules |
| --- | --- |
| Returned record, seven output obligations | `PosteriorOutputSolver`, `CachedPacketOutput` |
| Successful-return soundness and universal successful termination | `CachedPacketOutput`, `CachedPacketSolver` |
| Exact factor-coded covariance model | `RationalCertificateChecker`, `RationalModelSemantics`, `GramNoiseFloor` |
| Actual Bayesian target and a.e. canonical version identification | `FDGaussianConditioning`, `FDPosteriorKernel`, `FDForwardJointLaw`, `FDReverseJointLaw` |
| Coupling cost, residual gain identity, distribution error | `FDInexactGainCoupling`, `FDResidualEnergyCertificate` |
| Four complete rational projector obligations, real interpretation | `RationalPacketCertificates`, `PacketSelectiveAlgebra` |
| Arbitrary finite candidate checks and semantic tolerance | `RationalCertificateChecker`, `RationalPosteriorCertificate` |
| Output-selective locality, input-coupling boundary | `PacketSelectiveAlgebra` |
| Executed finite maximum scan, ties, coverage, energy share | `GreedyPacketSelection` |
| Adaptive geometric rate and explicit rational fuel | `GreedyPacketConvergence`, `GeometricFuel` |
| Exact cache initialization, selected update, preservation | `CachedPacketState` |
| Cached score/gain equality with recomputed trajectory | `CachedPacketState`, `CachedPacketTrajectory`, `CachedPacketOrigin` |
| Bounded search soundness/origin/completeness | `CachedPacketSearch`, `CachedPacketSolver` |
| Outward scalar and matrix enclosure construction | `RationalBall`, `DyadicBall`, `RoundedCandidate` |
| Sufficient final precision and finite probes with fallback | `PrecisionCompleteness`, `RoundedSolverSearch` |
| Joseph mean/covariance intervals and radius control | `PosteriorOutput`, `PosteriorOutputPrecision`, `PosteriorOutputSemantics` |
| Complete rectangular coordinate execution | `GeneratedCachedCoordinate` |
| Complete singular-prior rotated execution | `GeneratedCachedRotated` |
| Invalid independently rounded cache, final rejection | `CachedRoundingBoundary` |
| Separate genuinely rounded full-gain solver | `RoundedSolverSearch`, `RoundoffConvergence` |

## Fresh inventory and evidence distinction

Read-only invocation: `python3 scripts/lean_inventory.py`.
Result: **PASS**. Fresh checks cover:

- 939 manifest file entries, all digest matches.
- 117 active module identities and archived final successful receipt coverage.
- 117 current active-source before/after/staged digests, attempted-source snapshots, and archived process-log digests.
- 288 direct project dependency records, current dependency source digests, and cross-receipt agreement of recorded compiled-output hashes.
- 543 named theorem/lemma declaration locations, complete axiom-audit coverage, and corresponding source digests.
- Axiom union exactly `Classical.choice`, `Quot.sound`, `propext`.
- 94 actual source excerpt texts, line spans, and SHA-256 digests.

**No fresh Lean compilation ran.** The pinned Lean 4.34.0-rc2 runtime and mathlib commit were unavailable in this publication session. The source archive preserves zero `.olean` payloads. Their recorded output hashes agree across dependency receipts, but absent compiled files cannot be independently rehashed here. Archived kernel evidence is distinguished explicitly from fresh read-only consistency checks in the cover reading contract, rebuild section, and appendix.

The declaration inventory has 543 entries, including support lemmas and concrete/benchmark checks. This is not reported as 543 independent discoveries. The 21 benchmark modules certify static explicit candidates; the two generated modules certify actual canonical program returns. The universal algorithm proofs supply separate evidence. The September build reused pinned mathlib compiled caches and does not claim to have rebuilt all external dependencies from source.

## Conservative mathematical self-review

Coverage: all newly authored prose, displays, listing locators, commands, module map, and source-excerpt generation. Source proof bodies were retained unchanged and mapped byte for byte. Every applicable source hash remains equal to the archived manifest.

- Routine edits: corrected the excerpt extraction endpoint for adjacent single-line declarations, removing duplicate subsequent declarations and namespace endings; mapped Lean Unicode glyphs explicitly for pdfLaTeX listings; checked spelling, cross-module names, hypothesis wording and numerical interpretation.
- Mathematical-token changes to archived proof/source: **none**.
- Correction to new explanatory prose: the rotated approximate Joseph covariance coefficient is `130379/390625`, obtained from `1 - 4*(203/625) + 6*(203/625)^2`. An initial handwritten `130459/390625` transcription was corrected before delivery. The archived theorem excerpt and certificate data were unchanged.
- Explicit version boundary: successful returns certify the chosen explicit Gaussian posterior kernel at the supplied observation. Agreement with Mathlib's canonical posterior is evidence-almost everywhere.
- Explicit operational boundary: `certifyRounded` executes `checkSetup`, the outward candidate graph, and `checkTolerance`; it proves exact `checkCandidate = true` by construction soundness without executing a full exact residual recomputation.
- Explicit parameter boundary: output intervals enclose the certified approximation's parameters, not exact-posterior coordinates and not a separate interval-center Gaussian.
- Explicit arithmetic boundary: exact selective updates, outward final evaluation, and the separate rounded full-gain branch are not conflated.
- Unresolved mathematical issues in this authored scope: none found in conservative self-review. Independent publication audit is recorded separately. The final 29-page rendered companion passes the complete visual/structural review in `lean_visual_review.md`; layout-only changes preserve all source excerpts and mathematical content.

