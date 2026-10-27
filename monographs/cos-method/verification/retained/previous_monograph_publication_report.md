# Publication and verification report

## Deliverable

The monograph contains 121 pages, four parts, twelve chapters, and four appendices. Its visual atlas contains an opening pipeline and 17 numbered studies. The PDF has 97 bookmarks and 185 links.

All 121 pages were rendered with PDFium. Page images and contact sheets were reviewed for layout. A separate text-bounds check found no words outside the page. There are no blank text pages, unresolved references, missing-glyph warnings, replacement characters, or overfull boxes. Six underfull table-cell warnings remain. These concern spacing, not clipping.

## Executed numerical checks

| Group | Tests | Result |
| --- | ---: | --- |
| Structural | 31 | Pass |
| Signed and noncentral | 8 | Pass |
| Interval backend | 3 | Pass |
| Accuracy controller | 2 | Pass |
| Verified spectrum | 4 | Pass |
| Directed contract | 10 | Pass |
| **Total** | **58** | **No failures, errors, or skips** |

The engine source was unchanged during the replay. Delivered engine files were also compared with the replayed source.

The scaled chi-square control near 10^-5000 met a requested relative tolerance of 10^-18. Its directed probability-interval ratio-minus-one was approximately 9.201415e-20. An independently evaluated exact finite Erlang interval was fully contained.

The exact binary64 64-by-64 matrix control near 10^-16 met a requested tolerance of 10^-12. Its achieved ratio-minus-one was approximately 2.782939e-15. All 64 independently known eigenvalues lay in the computed spectral intervals.

These two controls do not imply a certified fast path for every spectrum, signed form, rank, or application model. The book keeps those restrictions explicit. Full original numerical results, precision settings, and source hashes are in `verification/numerical_replay/`.

## Mathematical editing

The source inventory contains 61 numbered environments. All 61 remain in the integrated manuscript. Two proofs were added. One source theorem was corrected: exact range capture preserves the nonzero spectrum, but an enlarged captured subspace may add zero eigenvalues to the core. The stronger assertion about the entire core spectrum needs an exact-range hypothesis.

An exact rank-one counterexample demonstrates why the qualification is necessary. A separate three-dimensional worked example verifies the corrected equivalence. Both were checked using symbolic arithmetic. See `verification/check_range_core.py` and `verification/range_core_correction.json`.

The numerical engine was not changed by this correction. A statement-inventory comparison does not establish that every mathematical proof has been independently formalized.

## Lean status

The retained project records acceptance of 26 theorem declarations and eight definitions, with a 34-declaration axiom audit. No new Lean compilation was executed in this publication pass. The book does not describe retained compiler evidence as newly reproduced.

The formal companion covers finite Gram algebra, block refinement, streamed identities, coefficient order, and arithmetic consequences of valid enclosures. Gaussian reduction, inversion analysis, spectral enclosure construction, and interval-library correctness remain outside that formal scope.

## Recovered build and inspection issues

The initial LaTeX build encountered an invalid package-date option. Removing that invalid option restored compilation. An initial full-document inspection with a slower renderer timed out and was replaced by a completed PDFium render. The text-bounds XML parser rejected control characters emitted by the text extractor. Removing those XML-invalid control bytes from the inspection copy allowed the bounds check to complete. The PDF itself was not altered by that parser repair.

All reported numerical checks completed. No failed mathematical or numerical test was omitted from the recorded replay. The remaining explicit limitation is that Lean was not rerun and neither the publication check nor finite tests prove end-to-end implementation correctness.
