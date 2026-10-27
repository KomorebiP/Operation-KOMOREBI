# Expanded reader edition 1.1: authoring and release report

8 October 2026. Publication author: Komorebi P. Series: Operation Komorebi.

## What changed

The first edition was too brief for the requested conjecture pieces and omitted the separate visual guides. This edition expands both manuscripts with worked derivations, examples, explicit hypotheses, reading maps, and complete finite tables. It also supplies one independent companion visual guide for each conjecture. The final reader set has two 27 page monographs and two 25 page guides. Each guide has a cover and 24 distinct illustrated spreads.

Collatz now develops the ordered affine offset, the endpoint parity bit, source dependent descent thresholds, composition, delayed descent families, progression lifts, all 42 states in the odd orbit from 27, the three iteration clocks, and a finite version of the common height packing argument. Riemann now develops heat convergence, scalar and Hilbert valued Laplace arguments, exact Fourier and Gaussian constants, Hermite and Poisson calculations, finite signed prime cubes, squarefree support, the full absolute majorant barrier, and the exact remaining signed estimate.

The illustrations are produced with Python and Matplotlib. Integer and rational quantities are computed exactly where stated. Decimal and binary64 calculations are identified as numerical. Hypothetical zeros, model energy curves, and proof capacity comparisons are labeled as models or schematics. Each visual spread has a reading column and a carry forward statement.

## Recovery and evidence

The transient working folder from the first edition was unavailable. The saved source archive was recovered, and all 83 original payloads were checked against their recorded SHA256 hashes before work continued. Original sources, audit reports, and reader PDFs are retained under `archive/v1.0/`. Evidence files were retained without silent correction. The original acquisition limits are recorded in `shared/LITERATURE_CHECK.md` and the manuscript source registers.

The expansion adds explanations and finite controls, rather than a new external theorem dependency or novelty claim. Inaccessible original Terras and RH archive sources remain inaccessible in the historical record. Selected recovered Lean text is retained as evidence. This is not a complete portable Lean dependency project, and no fresh Lean build or historical residue enumeration is claimed.

## Mathematical review and computational scope

`shared/REVIEW_v1.1.md` pins the four body revisions reviewed in full. Its obligation matrix and exact control report record the scope of the independent reconstruction. The final version 2 bounded run is in `shared/review_expansion_final_run/`. The initial run with fewer controls is superseded and excluded from the release archive.

Independent controls include ordered word cylinders, the three clocks for 27, the 165 offset example, progression lifts, rational density bounds, squarefree support, finite prime cube regrouping with a fixed cutoff, positive tail controls, Hermite Gram entries, Gaussian square completion, Poisson calculations, and finite c_K values using a different Bernoulli recurrence and Machin evaluation of pi. Each guide also preserves its own generator, data, computational scope, environment, and output hashes. Final manifest checks and source checks passed. These finite calculations are not universal proofs.

Collatz still requires universally produced actual descent below the original source. The bounded deficit exclusion is proved only under its stated permanent coefficient noncrossing and common height hypotheses. Riemann still requires the signed arithmetic estimate at every scale, or the equivalent subexponential energy input. The absolute majorant barrier does not give a lower bound for the signed coefficient. Neither conjecture is claimed solved.

## Resolved failures

The failed and superseded steps are preserved here and in the local authoring and proofreading notes.

1. Both paper builds initially requested the unavailable EC typewriter font `ectt1095`. The shared template now uses installed Courier. A resulting long identifier exceeded a line. Break opportunities after its underscores corrected that overflow without changing its printed name.
2. Both initial guide builds lacked the `ShortTitle` macro used by the shared header. Supplying the two titles corrected the build. A layout check launched after the failed build found no compiled guide PDF and failed. The check was rerun after successful compilation.
3. Cover and body page anchors initially had duplicate identifiers. Cover anchors are disabled and body anchors restored. Final logs contain no duplicate destination warning.
4. One temporary Collatz arithmetic check had an indentation error. It was corrected before any passing result was recorded. A Riemann text patch initially failed to match its context and was reapplied to the actual source.
5. A Riemann plot label used unsupported overline syntax. Braced notation corrected it. The compression rate chart initially included the boundary q = alpha despite a strict domain in its title. It now begins above alpha.
6. The first Collatz figure run stopped because a symmetric log threshold was passed through an unsupported API. Moving it to `set_yscale` corrected the failure and a complete regeneration passed.
7. The largest odd orbit state was initially annotated at manually entered step 17. Review identified step 32. The final arrow coordinate is computed from the actual maximum index.
8. Collatz figure footer prose collided with axis labels. The redundant footer prose was removed from the graphics and retained in the data and adjacent guide text. Fitted margins corrected clipped vertical labels, endpoint markers, and historical coverage labels.
9. A prime cube display in the Riemann reading column initially exceeded the column by 6.618 points. Its aligned line break corrected the overflow without changing the equation.
10. The Riemann bibliography initially continued onto a nearly empty final page. A small reference font brought the complete references onto page 27 without changing their content.
11. A report sentence incorrectly called 25 and 49 squarefree rows. They are nonsquarefree with zero Möbius coefficients. Their computed values were correct. The report wording was corrected and its manifest checked again.
12. Review supplied omitted domains and conventions in the Collatz merger and density spreads, and in the Riemann compression and K = 0 descriptions. Those body revisions were reviewed again and their hashes pinned.
13. The first final save batch returned a definite transfer failure for the Riemann visual guide. The other four outputs succeeded. Only the failed guide was retried, and the source archive was revised to retain this failure record. This transfer failure did not affect its compiled PDF or mathematical checks.

No unresolved arithmetic failure was found in the declared finite ranges. That statement concerns those controls, not the conjectures. No failed source acquisition was turned into a verified source claim.

## Production verification

All four PDFs compile twice with pdflatex and are rendered to page images. The complete sets of page images were inspected through contact sheets, with full page inspection of detailed tables, equations, plot labels, and the final references. The final Collatz figures were rebuilt after margin corrections and their assembled pages inspected again.

The final layout record is `shared/LAYOUT_VALIDATION_v1.1.json`. There are no unresolved overfull boxes, undefined references, missing glyphs, duplicate page anchors, words outside the page, replacement characters, or draft placeholders. `shared/SOURCE_VALIDATION_v1.1.json` records current source checks and hashes. Small underfull spacing messages can remain and do not represent clipped or missing material.

The source archive includes the four reader PDFs, the final sources, vector and raster figures, reproducible scripts, data, selected recovered evidence, and audit reports. `MANIFEST.json` lists payload hashes. Packaging checks both ZIP integrity and every listed payload hash.
