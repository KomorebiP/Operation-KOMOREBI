# Signal Lean guide review

Author of the publication: **Komorebi P.**  
Edition: **October 6, 2026**.  
Verdict: **source correspondence and disclosed evidence boundaries pass the current review**. No fresh Lean elaboration or kernel check was performed for Signal.

The canonical guide is `lean/Signal_Reconstruction_Lean_Guide.md`, `.tex`, and `.pdf`. It was generated from `lean/guide_content.md` and literal preserved-source excerpts by `lean/build_lean_guide.py`. It explains actual related formal objects and their hypothesis boundaries and maps all current SG claims to their remaining obligations. Markdown is included as an editable publication companion.

## Preserved source and provenance

The related source is the CRC-checked **Paper V v1.1.0 checkpoint**, archive `Paper_V_Complete_v1.1.0_With_Visual_Appendix.zip`, 23,437,514 bytes, 493 members, SHA-256 `7a15b94133739c26b8da5aadb2a2415c0bc539888430cec1baf0fb6425ea580e`. The later final archive was downloaded twice, with the same advertised size and SHA-256, but both copies failed ZIP validation. The cause is undetermined. The guide states that failure and names the checked fallback rather than implying that the later source was used.

The selected formal/verification subset contains no portable runtime and is not a complete Paper V distribution. The guide's future focused build commands use the pinned Lean v4.34.0-rc2 and recorded Mathlib revision; the original full verification driver expects additional original package content. These future replay commands are not reported as executed.

Current source inventories contain 23 production modules, 25 Lean files including root/audit, and 349 explicit declarations: 225 theorems, 107 definitions, seven abbreviations, nine inductive types, and one structure. The scanner includes `noncomputable` declarations and masks nested comments and strings. All production modules match the root import set. All 225 target names, files, lines and kinds agree with the inherited contract. The 827 historical namespace declarations include generated declarations and are explicitly distinguished from the textual count.

The archived build reports 3,296 jobs, including dependencies. The inherited axiom evidence allows `propext`, `Classical.choice`, and `Quot.sound`, with explicit no-axiom records accepted. The current static correspondence validates saved names and evidence; it is not a new compiler run. The current PATH probe found no `lean` or `lake`, and no fresh Signal build was attempted.

## Exact contract review

The guide's 19 source anchors are literal slices of preserved files, with qualified names, file hashes, source line ranges, context hypotheses, and a separately labeled interpretation. Some excerpts stop at a theorem type/proof delimiter; they are not claimed to be standalone modules. The full raw proof is bundled.

The review checked the following distinctions against the raw source:

- Coordinate packets require only the stated zero/equality structures; finite completeness requires an additive commutative coefficient monoid and a finite phase type.
- Integer addresses use signed Euclidean division, with `N > 0` in the inverse laws. A channel delay is an original delay `N*d`; general delay has a signed carry.
- Hilbert packets are actual complex ℓ2 vectors and bounded linear maps. Their output uses joint ℓ2 on `Fin N × ℤ`. The norm-convergent impulse expansion concerns sequence-coordinate vectors, not continuous Dirac measures.
- FIR transfer has finite support and exact finite channel sums. The general ℓ1 convolution theorem in SG-05 requires additional absolute-convergence reasoning. Laurent bank reconstruction is an all-input operator criterion; transform formulas retain their convergence assumptions.
- `KomorebiPaperV.known_edge_error` has arbitrary `Q : E → E` and supplied `j`. Its filename does not insert a `KnownEdge` namespace. It supplies no unknown-edge estimator or Fourier approximation rate.
- Mask estimates use extended `eLpNorm`, measurable masks, and the stated exponent hypotheses. Ordinary real norm translations require finiteness. The infinity estimate uses actual empty symmetric difference, not measure-zero symmetric difference.
- Finite complete-pruning synthesis assumes conservation and an identity root. The additive evaluator's work bound is an abstract unit-cost model with supplied node costs. Finite attainment for arbitrary coupled objectives does not prove the same dynamic program computes them.
- Frequency offsets in the Signal model are integers; unknown node locations are continuous. The integer coordinate formalization does not establish phase estimation or associated-root branch selection.
- Exact mathematical ridge stationarity is `Mᵀr = λc`; numerical execution checks this within tolerance. Clipping remains nonlinear, and the residual archive retains the entire residual.

## Current Signal mapping

`lean/Claim_Lean_Concordance.json` and `.csv` contain all 46 current SG IDs. The map copies `claim_id`, `title`, `statement_tex`, `hypotheses`, `hypotheses_tex`, and `domain` exactly from the frozen `traditional/Claim_Concordance.json`, SHA-256 `ffe0b1ee413da77fd443669d97634ac3817fbd1236c4a22af30eaf35daf0b535`. `lean/CLAIM_MAPPING_AUDIT.json` records this input identity and field-parity check. Every related declaration has an exact qualified name, source path, line, source SHA-256 and quoted type header.

Sixteen SG claims have related narrower infrastructure; thirty have no recovered target in the inspected Paper V corpus. **No whole current SG claim is labeled as fully formally covered.** This is deliberately conservative: arbitrary algebraic packets, continuous Fourier models, sparse residualized injectivity, Prony rank/roots, root matching, thresholded order recovery, frequency-offset calibration, normalized periodic integration, and the current global reconstruction rate are broader than the saved target statements.

The map includes the final SG-28 singular-value minimax explanation, SG-38 normalization of real recovered amplitudes to zero total jump, and SG-40's unambiguous offset variable. The corrected zero-mean L1 location term, capped spark convention, fixed-order location witness, zero-order theorem branch, representative convention, bounded linear synthesis, and strict branch-margin requirements are retained.

The guide preserves the largest-ratio rank counterexample and distinguishes it from the valid supplied-threshold theorem. It discloses the complex benchmark's six-versus-nine order mismatch and infinite unmatched parameter errors alongside finite improved synthesis RMSE. It distinguishes the rank-aware dictionary execution copy from the original QR/compact-SVD code. The native positive-order `EdgeModel` and `recover_unknown_edges` API still exclude order zero; the theoretical zero branch is not represented as a newly added wrapper.

## Publication checks

The guide builds successfully through all three deterministic pdfLaTeX passes using `build_release.py --only lean`. The final third-pass log contains no overfull/underfull boxes, undefined references, missing characters, or warnings. The PDF has 24 pages and correctly identifies Komorebi P. as author.

All 24 pages were rendered for review. Three contact sheets were inspected, followed by enlarged source/formula pages. The code excerpts are kept together; table headers repeat on continuation pages. Text bounds lie within the safe page region on every page. The bounds audit is `reviews/LEAN_PDF_BOUNDS.json`; page renders and contact sheets are in `reviews/lean_visual/`.

The source anchor, inventory and map scripts are portable relative to the release root. Their output explicitly states that it is static inspection. Current guide generation and publication are reproducible without inventing a fresh formal certificate.
