# K-COS monograph: closing editorial and verification report

## Final publication master

**The K-COS Method** is closed as a **138-page publication master**, with four parts, twelve chapters, four appendices, seventeen numbered visual studies, and fifty vector graphics. It has 144 bookmarks and 156 links. This edition supersedes the earlier monograph PDFs and preserves the latest vector-figure design.

“Closed” describes the delivered editorial and production state. It does not claim that every mathematical or software layer has been formally verified. The book retains the implementation and formalization boundaries stated below.

## Editorial and mathematical refinements

The complete change record is `verification/closing/editorial_changes.json`, with a unified source diff in `source_changes.patch`. The pass includes 88 recorded substitutions. Some later substitutions refine an earlier layout decision; this is an edit ledger, not a count of distinct defects.

The substantive refinements are:

- The pruned operator is defined explicitly before its transfer matrix is used. The equal-cost pruning argument specifies a nonnegative budget, allows the empty selection, and handles the case in which every candidate pair is feasible.
- The complex cumulant generating function is defined through the individual factor logarithms and its analytic normalization at zero. The packet proof and atlas identify the logarithm branches rather than relying on an unspecified logarithm of the full transform.
- The analytic packet calculation is kept distinct from the implemented direct-spectrum interval backend. A structural or analytic bound is not promoted to a numerical enclosure. Spectral endpoint calls must satisfy the selected backend’s domain and rank conditions.
- Algorithm notation now consistently uses the book’s support endpoint and mode count. The independent inversion’s decay exponent no longer shares the probability symbol. Gaussian-law, iteration-equivalence, and memory-model assumptions are stated where used.
- The synthetic rare-variant study defines its effective-rank statistic, minor-allele weighting, and residualization order. The stored run called “fine 64” is distinguished from its actual count of 32 blocks.
- The executable appendix imports its tail routine and initializes a floating accumulator even when the input vector has integer dtype. The listing was executed directly in finite controls.
- Redundant transitions and isolated scalar displays were tightened. Worked calculations, concluding paragraphs, captions, and atlas reading connections were reflowed to remove short spillover pages without shrinking or replacing the scientific graphics.

All **61 numbered source environments** remain: 35 theorems, 12 corollaries, six propositions, two lemmas, five remarks, and one algorithm. All **39 proof environments** remain. Four statement/proof environments were edited; their before/after hashes and labels are listed in the audit. All baseline labels are preserved. These inventory checks do not independently validate an argument.

## Preserved material

The audit compared **150 engine/data files** and **31 Lean-project files** with the technical baseline. None changed or disappeared. All **150 publication-graphic assets** (50 PDF/SVG/PNG sets) match the latest figure-edition archive byte for byte. The final book has no embedded raster graphics. Figure-input hashes still match the retained data. No empirical vector or new timing measurement was invented.

## Fresh numerical replay

| Regression group | Tests | Outcome |
| --- | ---: | --- |
| Structural | 31 | Pass |
| Signed and noncentral | 8 | Pass |
| Interval backend | 5 | Pass |
| Accuracy controller | 2 | Pass |
| Verified spectrum | 4 | Pass |
| Directed contract | 10 | Pass |
| **Total** | **60** | **No failures, errors, or skips** |

The replay used the supplied engine and recorded its commands, environment, elapsed times, and source hashes. Source hashes before and after execution agree. These are current executions, not restatements of the earlier figure-pass results.

Both independent controls passed. The scaled chi-square control near `10^-5000` met its requested `10^-18` multiplicative tolerance, with directed ratio upper bound approximately `9.201415e-20`. An independently evaluated exact Erlang interval was fully contained. The exact-binary64 64-by-64 matrix control near `10^-16` met the requested `10^-12` tolerance, with ratio below `2.783e-15`; all 64 independently known eigenvalues lay in the computed spectral intervals.

Complete outward decimal endpoints and input semantics are in `verification/closing/numerical/controls.json`. Rounded summaries in this report are not the authoritative endpoints.

## Fresh worked-example and finite checks

The dyadic factor example was rerun in an isolated working directory, so historical results and publication graphics were not overwritten. Its exact algebra, law, saddlepoint, and six packet-remainder comparisons passed. For the spectrum `(1,1,2,2)` at `q=40`, the independent exact law is `2 exp(-10) - exp(-20)`. The first fixed resolution correctly fails the requested 2% width, the refined resolution passes, and its enclosure contains the independent closed-form interval. The same fixed refined enclosure correctly rejects a 0.1% request.

The eight retained symbolic controls passed, including the oversized-range, QR, residual-completion, compressed-frontier, zero-padding, singular-noncentral, and shared-polynomial cases. The separate range-core symbolic check also passed.

Three additional control groups passed: 25 exact-rational pruning examples covering empty/all/zero-risk cases, execution of the actual appendix listing on vector and matrix inputs with and without projection, and reproduction of the memory table’s declared tile parameters. These are finite controls, not general proofs by enumeration.

## Publication checks

All **138 final pages** were rendered with PDFium. The page sequence was reviewed through contact sheets, with enlarged inspection of the reflowed worked examples and verification page. No clipping, collisions, or stray one-line pages remained in that review. All fifty figure assets are single-page vector PDFs with editable SVG counterparts and PNG previews.

The final build has **zero unresolved-reference, unresolved-citation, duplicate-label, missing-character, overfull-box, underfull-box, or warning diagnostics**. Programmatic checks found no empty pages, words outside page bounds, invalid internal link destinations, or invalid bookmarks. Fonts were inspected; no font binaries are distributed. A successful geometry check is not a guarantee that no human reader could prefer a different typographic choice.

The delivered SHA-256 manifest covers the package bytes. ZIP integrity and manifest verification are recorded separately in the final packaging result.

## Recovered production issues

An attempted interactive execution session was unsupported and launched no numerical work. Ordinary subprocess execution completed the replay. An initial editing-script match failed because a Python string interpreted a LaTeX escape; the baseline was restored before the corrected transactional editing script was applied. The final source scan contains no invalid control characters.

Intermediate page review exposed orphaned final paragraphs, a reading connection on a separate page, and an isolated worked-example figure. These were corrected by local rewriting and reflow, then the book was rebuilt and rerendered. The deliberate failed-tolerance case in the running example was retained rather than relabeled as a pass.

## Limits and final status

**Lean was not recompiled.** Neither `lean` nor `lake` was available in the closing environment. The 26-theorem, eight-definition companion and its historical compiler/axiom records remain unchanged and are explicitly identified as retained evidence.

The directed numerical guarantees remain conditional on the stated interval arithmetic and transcendental implementation. Signed and noncentral numerical paths do not inherit the positive directed backend’s guarantee. The dense matrix-to-spectrum verifier, low-rank restrictions, and unverified preprocessing boundaries remain explicit. There is no new native-GPU benchmark, universal speedup theorem, or end-to-end formal proof of the numerical implementation.

The editorial, figure-preservation, numerical-replay, and publication checks recorded here are complete. The delivered PDF and matching sources are the final publication master.
