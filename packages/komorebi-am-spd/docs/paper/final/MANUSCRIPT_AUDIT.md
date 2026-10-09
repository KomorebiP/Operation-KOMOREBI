# Final manuscript audit

## Status

The manuscript was rebuilt as a focused, publication-style research paper. The finalized edition is 78 letter-size pages. It contains a one-page table of contents, nine principal sections, four historical appendices, 85 Python-generated vector figures, corrected result tables, and 13 bibliographic entries.

This audit establishes editorial consistency, source-to-table traceability, successful LaTeX compilation, PDF integrity, and replay of the supplied verification suites. It is not a substitute for independent peer review and does not certify novelty or every mathematical claim beyond the arguments and tests present in the manuscript.

## Structural revision

- Reduced the archival manuscript from 147 pages to 78 pages.
- Removed approximately 70 pages of embedded Python listings. The executable code remains in the GitHub repository.
- Replaced the three-page fragmented contents list with a one-page contents page and a conventional section hierarchy.
- Moved the final AM-SPD method and principal results ahead of historical development experiments.
- Retained the packet-core, SPD/SVD, and two-seed studies as clearly labeled appendices.
- Rewrote the abstract to remain below 200 words by plain-text counting.
- Restored a focused bibliography covering low-rank approximation, best-basis selection, matching pursuit, Gibbs reconstruction, finite-rate innovation, edge detection, segmentation, superpixels, perturbation bounds, and the benchmark image source.

## Mathematical and technical corrections

- Separated ideal orthogonal least-squares projection identities from the recovered ridge-stabilized floating-point Gram solve.
- Replaced a continuous-boundary statement with a finite-raster partition theorem that matches the implemented object.
- Clarified that the integer-budget dynamic program is combinatorially exact on its declared finite state space while local costs are floating-point quantities.
- Restricted portfolio exactness to the finite candidates actually completed.
- Distinguished exact archive closure from sparse-model approximation quality.
- Added a caveat that dyadic density applies before discontinuous hard raster thresholding.
- Corrected scalar storage formulas for grayscale and RGB global SVD terms and for local rank packets.
- Distinguished exact RMSE from bounded RMSE after coordinatewise clipping to `[0,1]`.
- Replaced proof-oriented labels for computational tests with implementation-verification language.

## Principal result audit

The final tables were regenerated from the preserved JSON outputs rather than copied from prose.

| Image | Original SPD exact RMSE | Final exact RMSE | Final bounded RMSE | Exact reduction | Selected seed |
|---|---:|---:|---:|---:|---|
| Synthetic geometry | 0.0037262320 | 0.0031554670 | 0.0031554670 | 15.3175% | exact-budget tree |
| Synthetic text and curves | 0.0033944556 | 0.0031410838 | 0.0031410838 | 7.4643% | exact-budget tree |
| Camera | 0.0149429812 | 0.0050638376 | 0.0050638376 | 66.1123% | Lagrange tree |
| Astronaut | 0.0335527928 | 0.0107417699 | 0.0106905617 | 67.9855% | Lagrange tree |

The mean exact-RMSE reduction across the four declared cases is approximately 39.2%. These are finite benchmark results under the declared grammar, budgets, parameter proxy, and implementation. They are not universal image-compression or denoising guarantees.

## Verification replay

| Check | Result |
|---|---:|
| Installable-package tests | 10 of 10 passed |
| Package smoke verification | Passed |
| Core packet-atlas groups | 16 passed |
| Singular Packet Decomposition groups | 8 passed |
| Intermediate AM-SPD groups | 15 passed |
| Final implementation and stress groups | 11 passed |
| Implementation verification scenarios | 12,154 of 12,154 passed |
| Exact tree comparisons | 9,960 |
| Maximum reported property residual | below 1e-13 |

A first package-test invocation without installation or `PYTHONPATH=src` could not import `am_spd`. The documented repository invocation was then used, and all 10 tests passed. This was an environment-path issue rather than a failing test.

## LaTeX and PDF validation

- `latexmk` completed successfully.
- The final LaTeX log contains no LaTeX warnings, undefined references, duplicate labels, overfull boxes, or underfull boxes.
- The source contains no tab, carriage-return, vertical-tab, or form-feed control characters.
- The source contains no draft markers, AI disclosure language, or broken Unicode dash characters.
- The PDF opens successfully, is not encrypted, is text based, contains 78 letter-size pages, and has no form fields or XFA data.
- All fonts reported by `pdffonts` are embedded. Python-generated figure PDFs include embedded Type 3 subsets, which rendered correctly in the inspected output.
- All 78 pages were rendered at 180 DPI. No blank pages, clipping, overlap, black squares, or broken glyphs were observed in the inspected render.

## Preserved record

The original 147-page manuscript, exact source snapshot, scripts, figures, tables, results, and checksum ledger remain under `research/original` in the GitHub repository. The finalized manuscript does not overwrite that archival record.
