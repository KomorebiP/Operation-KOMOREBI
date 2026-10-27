# Traditional paper report

The completed traditional paper is **Signal Reconstruction: Polyphase Sampling, Unknown Edges, and Self-Calibration**, by Komorebi P., final edition October 6, 2026. It contains 46 principal result groups with statements, printed domains and hypotheses, and proofs. Its PDF is 31 pages. The editable TeX and the full mathematical Markdown manuscript are included.

The manuscript develops complete packet coordinates and transfer multiplication, finite refinement, transform packets, convolution polyphase kernels, and residual alias arithmetic. It treats the measurement/decomposition obstructions and a fixed-order collision counterexample. The reconstruction chain contains known-edge matched identification, the classical scaled Gibbs profile, residualized sparse dictionaries, exact unknown-order Hankel/Prony recovery, canonical periodic integration, conditional noisy root/amplitude bounds, internal offset phase recovery, strict branch lifting, an exact finite innovation budget, and conditional smooth-tail rates. The final synthesis uses a corrected mean-zero periodic L1 estimate. Shared locations, confluent terms, finite image models, ideal nested projection, ridge fitting, clipping, exact residual storage, and bounded completion have separate contracts.

The source concordance contains 55 hash-pinned lineage anchors. It marks newly reconstructed arguments and publication corrections. All 46 SG results have manuscript proofs; none is represented as a Signal-specific Lean-certified declaration. The related Paper V checkpoint is described as supporting infrastructure under its own types. No fresh Lean run is claimed.

## Scope corrections and explicit boundaries

- Sparse uniqueness uses the kernel-secant condition, with the capped spark convention and the s=0 branch stated.
- Fourier exactness is for the integrable class and its selected right-continuous representative. The analytic background uses its canonical uniformly convergent Fourier-series representative.
- The collision obstruction compares two fixed-order, equal-amplitude narrow pulses at distant locations, using a permutation-invariant location distance.
- Root disks control complex roots. Angular location bounds require normalization and chord-to-angle conversion. The Rouché gate uses true centers and errors, and is not a data-only certificate.
- Offset products require a nonempty adjacent product set. Branch spacing requires N at least two. Rank zero and full rectangular rank are handled separately.
- The finite self-calibration budget is conditional on a supplied noncolliding decimation and excludes the low Fourier modes. Conditional rates hold on admissible selected scales, with uniform local inverse bounds and an explicit branch margin, including p=0.
- The periodic mean-zero L1 bound with location coefficient one is refuted. A translated-sawtooth proof gives the sharp additive bound, with amplitude coefficient T/4 and location term 2d(1-d/T). Its counterexample is printed.
- Estimated amplitudes are made real and zero-sum before canonical edge integration in the global L1 rate theorem. The normalization preserves the stated error order.
- Confluent annihilation does not imply the displayed order is minimal when leading coefficients vanish. Phase ratios require nonzero leading coefficients. Simple-root stability is not transferred to repeated roots.
- Ideal exact least-squares projection is separated from positive-ridge stationarity, nonlinear clipping, and truth-residual archival reconstruction.

## Finite evidence and implementation boundaries

The current evidence is ten bounded suites with 288 recorded checks and 281 checks after the stated duplicate exclusion. It includes reproduced recovery failures: the localized burst model infers nine jumps for six true jumps, and the largest-ratio witness infers order two for a true rank-three model although an admissible supplied threshold selects three. Improved waveform RMSE is explicitly separated from correct parameter recovery. The initial overstrong complex-stress replay check and its failure remain disclosed.

The original numerical generic projector/rank helper caveats and the separate rank-aware execution copy are explained. The zero-edge theorem branch is not represented as a newly implemented zero-edge wrapper. The full-image input, finite store caps, positive ridge, truth residual, clipping scope, and invalid zero method-time fields of the infinite-packet program are reported.

## Publication verification

The root deterministic build command completed three TeX passes. The current log has no overfull/underfull boxes, unresolved references, font warnings, or missing glyphs. Every text span lies within the checked page safety bounds. All 55 source anchors match the current preserved bytes. The Markdown contains all 46 statement/proof groups and **73 display equations**, identical to the TeX body modulo whitespace and the required align* to aligned wrapper conversion. The Markdown includes the bibliography and usable citation links.

Twelve representative pages were rendered. The cover, packet blocks, Gibbs derivation, root-disk bound, finite-budget proof, corrected L1 bound, ridge scope, computation table, source appendix, and references were visually inspected. The references are kept together on the final page. PDF/source hashes and exact bounds are in `traditional/PUBLICATION_QA.json`; `traditional/verify_document.py` reproduces these publication checks.

A late publication check caught a 49.7552-point overfull line caused by the newly added inline complex singular-value min–max formula. It was converted to a display and rebuilt. The final log and bounds checks pass.

## Final conservative proofreading

Reviewed the complete authored manuscript, its generated Markdown, source concordance, and rendered representative pages under the proofread-math self-review instructions.

- Routine edits: theorem wrapper formatting, bibliography conversion, Markdown equation blocks, citation links, source-lineage typography, and one long inline formula moved to a display.
- Mathematical-token changes during final conservative proofreading: none. The substantive domain and contract corrections above were authored and audited before the final proofreading pass.
- Unresolved proofreading issues: none found in the reviewed scope.
- Validation: deterministic three-pass TeX build and the publication checks passed. The independent mathematical reviewer separately inspected all 46 claims. A proof review and finite numerical replay do not constitute Signal-specific formal verification.
