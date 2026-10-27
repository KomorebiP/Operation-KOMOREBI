# K-COS revision and verification report

## Delivered edition

The rebuilt monograph has **139 pages**, four parts, twelve chapters, four appendices, seventeen numbered visual studies, **144 bookmarks**, and **156 links**. The technical baseline is the corrected 122-page source, not the earlier 138-page design branch. Its corrections are retained while the professional book design is applied throughout.

## Editorial and design changes

The revision replaces the crowded detailed contents with a two-page chapter map and preserves deeper navigation in bookmarks. A separate inner title, white part openings with linked chapter maps, restrained aubergine cover, serif display headings, quieter headers, and consistent table and caption typography form one design system. The preface and reading guide were rewritten, chapter openings supply the role of each stage, and selected worked sections are held together rather than spilling a few lines or a lone figure onto the next page.

The transform uses kappa for the cumulant, b for the support endpoint, N for the COS mode count, and J_k for the payoff coefficient. The visual studies use the same notation. Appendix C maps the older source variable names. Local linear-algebra meanings remain explicitly defined.

A recurring dyadic 4-by-6 factor has spectrum (1,1,2,2). The text follows its exact block actions, distribution, tilt, packet representation, and directed tail calculation. A separate packet with four declared coefficients illustrates nonzero approximation error. The exact range-core example now includes an explicit oversized-basis counterexample, making the nonzero-spectrum qualification visible rather than leaving it as an editorial warning.

Fourteen charts were redrawn from retained CSV measurements or sizing data. Two additional figures belong to the new explicit example. Redraw source hashes and limitations are recorded in `redrawn_figures.json`. No retained measurements were relabeled as new timings. Missing raw vectors for two older rank/QR illustrations were not invented.

## Source preservation

The current source contains the same **61 numbered source environments** as the corrected baseline: 35 theorems, 12 corollaries, six propositions, two lemmas, five remarks, and one algorithm. All **39 proof environments** remain. No baseline chapter-source label is missing. The diff records notation changes and added exposition.

The audit compared **150 engine/data files** and **31 Lean-project files** with the technical baseline and found no changed or missing file in those sets. This retains the earlier interval-width reporting correction, QR/range/residual spectral qualifications, and frontier-coordinate correction. A count, diff, or hash does not independently verify a mathematical argument.

## Fresh numerical replay

| Group | Executed tests | Failures / errors / skips |
| --- | ---: | --- |
| Structural | 31 | 0 / 0 / 0 |
| Signed and noncentral | 8 | 0 / 0 / 0 |
| Interval backend | 5 | 0 / 0 / 0 |
| Accuracy controller | 2 | 0 / 0 / 0 |
| Verified spectrum | 4 | 0 / 0 / 0 |
| Directed contract | 10 | 0 / 0 / 0 |
| **Total** | **60** | **0 / 0 / 0** |

Both existing independent controls passed. The exact-spectrum scaled-chi-square control near 10^-5000 met the requested 10^-18 multiplicative tolerance, with ratio-minus-one approximately 9.201415e-20 and the independent Erlang interval contained. The exact-binary64 64-by-64 matrix control near 10^-16 met its requested 10^-12 tolerance, with ratio-minus-one approximately 2.782939e-15 and all known eigenvalues inside the spectral intervals. Full decimal endpoints, commands, timings, hashes, and precision settings are in `numerical_replay/`.

The eight retained exact algebra controls were executed successfully, as was the separate range-core symbolic check. These are finite symbolic examples and negative controls, not general proofs by enumeration.

## New running example

For q=40, the independently evaluable survival probability is

`2 exp(-10) - exp(-20) = 0.00009079779837134726451335506518072106465...`.

The packet study uses coefficients (1.96,1.98,2.02,2.04) at 0.1+0.4i. Six moment orders were evaluated at high precision, and each observed discrepancy lay below its analytic remainder bound. The plotted and tabulated comparisons are rounded point evaluations, not directed interval certificates.

For the directed calculation on spectrum (1,1,2,2), b=512, eta=0.245, and 60 interval digits, N=8192 gives a relative-ratio upper bound approximately 0.0246130 and **does not meet** tolerance 0.02. N=16384 gives approximately 0.01372914 and passes. The readable outward log10 interval is [-4.04489575,-4.03897381]. Its coarser width also meets 0.02. An independently evaluated interval for the closed form is fully contained. The same fixed enclosure correctly rejects tolerance 0.001.

`worked_example.json` includes both mode counts and their decisions. Exact algebra assertions check the factor, Gram matrix, spectrum, streamed action, survival density relation, and saddlepoint identity. The worked example is not a claim of efficiency on all low-rank inputs.

## PDF inspection

All 139 pages were rendered with PDFium. All contact sheets were visually reviewed, with selected corrected pages and figures inspected at larger resolution. A programmatic check found no words outside the page, no empty text pages, and no invalid internal link destinations. The final compilation has no unresolved-reference, duplicate-label, missing-character, overfull-box, or underfull-box diagnostics. Embedded fonts were inspected. Contact sheets and geometry/navigation results accompany the sources.

These checks do not guarantee that every typographic choice is ideal or that a human proofreader could find no further prose issue. They establish the specifically recorded checks. The figure source and table inputs remain available for independent review.

## Recovered failures and corrections during this pass

1. The initial attempt to use an interactive container session was unsupported. It executed no build. Ordinary subprocess execution was used successfully instead.
2. The first chosen mode count for the new example did not meet the assumed 2% tolerance. Its interval was valid but too wide. The failure was retained and the mode count increased, rather than weakening the tolerance. The final reproduction script tests both decisions.
3. Early layout builds exposed a long boxed formula, short spillover pages, and table-spacing warnings. These were corrected through reflow, explicit worked-section breaks, and ragged table cells. The final build is free of those diagnostics.
4. Source inspection caught a string-escape artifact in the notation table and an ambiguous rank reference introduced when a counterexample was inserted. Both were corrected before delivery. The final example identifies the rank-two first example separately from the rank-one counterexample.
5. Visual review found crowded plot labels and a buffering plot whose horizontal variable was constant in the retained data. The chart now identifies the five I/O/compute settings explicitly, each with 64 blocks. No data values were changed.

## What was not established

**Lean was not rerun:** neither `lean` nor `lake` was available. The delivered formal source and retained compiler records are unchanged. The historical 26-theorem, eight-definition, 34-declaration audit remains historical evidence, not a fresh build.

There is no new universal complexity or performance claim, new hardware benchmark, complete proof audit of every theorem, or end-to-end formal proof of the numerical implementation. Directed enclosures remain conditional on the interval arithmetic and transcendental implementation. The tests cover finite declared inputs. The existing implementation limitations for signed/noncentral paths, low-rank Fourier decay, and scalable matrix-to-spectrum verification remain in the book.

## Evidence locations

Current results are in `verification/current_revision/`. Earlier records remain under their original names and are not substituted for the current replay. `source_changes.patch`, `source_preservation.json`, `environment.json`, `redrawn_figures.json`, and `worked_example.json` explain the relationship between source, presentation, and execution. The delivered SHA-256 manifest and ZIP integrity check cover the packaged bytes, not mathematical truth.
