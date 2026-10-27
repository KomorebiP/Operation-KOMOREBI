# Independent H12 visual/source audit

**Status: complete. All 18 native figures and all 19 guide pages pass the independent source, data and layout review within the scopes below.**

Normalized claim: the H12 visuals preserve the retained definitions, plotted finite inputs, multiplicities, and scope. Primary mathematical-computation verdict: **computationally verified only in a stated range**. The infinite analytic statements require their separate source proofs; these finite checks do not prove the original arithmetic equality.

The reviewer read the raw v0.14 proof, relevant v0.13 divisor/transport/anchor proof, v0.12 principal-map definitions, and v0.6 four-line norm source before accepting the visual formulas. No author's QA verdict was used as a substitute for source or image inspection. Review is read-only with respect to the raw sources and `visual/` author files.

## Source and finite-input checks

- The chosen lower complex embedding is `β=∛7 exp(−2πi/3)`, with the retained `τ,t,s,δ`. Period signs and the multiplication matrices agree with the raw definitions.
- The actual support is the set with nonzero divisor coefficient, not the entire nondiscrete rank-three additive group. The strict-positive step function, ceiling pivot, smoothing weight and seven-residue lift are preserved.
- In the displayed chamber families, there are `n³` distinct order-four zeros and `4n³` distinct simple poles. Each side therefore has total multiplicity `4n³`. Neither the plots nor the audit infer cubic growth of the signed difference.
- All 2,197 triples in `[-6,6]³`, each with seven possible Fraction lifts, were independently checked. All 92,480 family points for `n=1,…,16` were checked for orders, distinctness, disjointness and chamber bounds. The 289-point ceiling/residue table and the finite line/cycle/coefficient tables also match.
- All 175 stored complex-coordinate records for `n=2,3` were recomputed using a separately implemented mpmath embedding at 110 digits, without importing or running the author's generator. The maximum difference is approximately `2.32×10⁻⁷⁹`, under the diagnostic tolerance `10⁻⁷⁶`. This is floating agreement, not an interval enclosure or a proof of universal injectivity.
- The canonical jet coefficients, reflection parity, transition coefficients, and conductor-three exponents `0,−2/3,−8/9` match the raw definitions. The four negative controls separate the intended formulas from the declared wrong alternatives.
- Genus three is sufficient and minimal for the **ungrouped absolute** construction. Special signed groupings are not excluded. The analytic tail estimate requires `n_D(r)≤Ar³` for every `r≥R_*`, `T≥R_*`, and `|z|≤T/2`. It yields `4A/T` for the weighted inverse-fourth-power sum and `2A|z|⁴/T` for the tail logarithm. Setting constants to one in an illustrative chart does not establish these infinite-support hypotheses numerically.

The active bounded independent run is `verification/runs/independent_visual_final_freeze/manifest.json`, with 44 execution inputs pinned before/after, 30-second wall, 20-second CPU, 512-MiB address-space, one-core and one-thread settings. It completed successfully and its v2 manifest validated against the frozen files. The earlier first-repair run is retained as explicitly superseded historical evidence; its hashes were not rewritten after the final spacing change.

## Native-resolution figure coverage

Every PNG was opened and inspected individually at its original resolution; contact sheets were not used to decide the verdict.

| Figure | Mathematical/data scope | Final native layout |
|---|---|---|
| 00 map | Comparison architecture; exact identification explicitly open | Passed after box-text wrapping |
| 01 periods | Fixed complex embedding and actual periods | Passed |
| 02 norm lines | Four exact order-three subgroups of `C₃²`; identity incidence four | Passed |
| 03 modulus/phase | Conditional relative phase factors; no evaluated discrepancy | Passed |
| 04 seven cover | Exact multiplication-by-four residue cycles; schematic placement | Passed |
| 05 ceiling | Declared finite pivot/digit box | Passed |
| 06 smoothing | Exact residue-five weight table | Passed |
| 07 chamber | Actual `n=3` family: 27 zeros, 108 poles; three-coordinate display | Passed |
| 08 complex families | Actual `n=2` rounded embedding: 8 zeros, 32 poles | Passed |
| 09 family counts | Distinct-point counts separated from multiplicity | Passed |
| 10 growth orders | Normalized scaling illustration; no measured theta/divisor data | Passed |
| 11 canonical jets | Exact local coefficients and illustrative real-factor curve | Passed |
| 12 tail bound | Analytic scaling profiles; no infinite-product evaluation | Passed |
| 13 ambiguity | Divisor matching alone versus the additional fourth-log identity | Passed |
| 14 reflection | Exact parity coefficient table | Passed |
| 15 transition | Exact polynomial difference and second derivative | Passed |
| 16 cube | Exact reconstruction exponents and relative lift ambiguity | Passed |
| 17 conjugation | Plane regularity separated from periodic/principal-norm and arithmetic obligations | Passed after wrapping and separation |

## Failures, repairs and preservation

The first native review found objective layout defects in 00 (two detail strings overflowed their boxes) and 17 (left title/detail overflowed, and the connector label crossed the top box edges). These were reported to the author and corrected by text wrapping and label placement. The corrected 00 was independently re-viewed. Corrected 17 was re-viewed after the first repair and again after the root requested more vertical space between its title and detail. Its final title/detail positions are separated and all text stays inside its boxes.

Only PNGs 00 and 17 changed from the individually inspected initial set; the other 16 PNGs are byte-identical. The initial generator/control snapshots were authenticated against the reviewer's earlier pinned hashes. The complete final `checks` dictionary is exactly equal to the initial dictionary. The generator diff changes only those labels/positions and introduces optional box text-position parameters; it does not alter the mathematics or numerical arrays. The five checked raw source files remain byte-identical. No unrecoverable source/data loss was found in this visual derivative set.

Final generator SHA-256: `12b63c73d88a292a46b43bf7164d2d08a67620b44a68173ff9836923c5e9e78c`.

Final control SHA-256: `5e19e57e2f8eb8ab0b6a6357bec0488839e459c7ebe0b048ddf3b12e786af74c`.

Final 00 PNG SHA-256: `410a8c936db2e66dd17a975d969a4eba986e2df6fd760e4630a759f06a8fc8ad`.

Final 17 PNG SHA-256: `0177bb9d6f8b2521c7246efefb61aa6312b54a9b4f6027c492c76dee0f47cb68`.

The companion JSON records every native PNG/PDF and raw-source hash, dimensions and coverage. Ordinary complex differentiation, canonical-product convergence and arithmetic comparison are not promoted to Lean proofs by these visual checks. No gamma/class-field equality, phase closure, numerical infinite-product evaluation or new interval certification is claimed.

## Guide review

The full guide's formulas and source-dependent prose were checked against the retained sources. Every page was individually inspected at 150 dpi using original-size page rasters. The reviewer independently rendered the final PDF with Poppler; no author page verdict was accepted as a substitute for inspection. All 19 pages are covered: 15 final page rasters are byte- and pixel-identical to individually inspected prior-revision pages; changed final pages 05, 08, 09, 11 were each directly re-viewed. Page 03's local arithmetic definitions, page 18's corrected conjugation wording, and page 19's explicit open-comparison scope were also individually inspected before this final exact-raster transfer.

Final PDF SHA-256: ec4eca6316c48ead20f5e7c42b86838f3727d1612825031968105ecf8056c19a (19 pages).

The review found and corrected these guide defects or needed clarifications:

- Arithmetic notation is now locally defined: epsilon_j and the retained algebraic involution iota, distinct from actual complex conjugation.
- Page 05 says “displayed gamma definition”; its newly displayed negative-period gamma and smoothed-theta definitions preserve the source conventions.
- Page 11 restricts the finite-theta grammar to fixed-period affine restrictions, finite derivatives and polynomial coefficients; the resulting numerator and denominator must both be not identically zero. The optional nowhere-zero entire prefactor is one global factor. Arbitrary such factors inserted inside sums are outside the class.
- Page 18 explicitly identifies the canceling canonical quotient W_D/W_D# as meromorphic. The remaining repaired quotient is entire and nowhere zero; those are distinct factors. The initial pronoun would have wrongly attributed meromorphicity to the entire factor, and was materially corrected.
- Pages 08/09 use larger 4.0in embeds for the genuine three-coordinate chamber and equal-aspect complex map. Labels are clearer, all text fits, and pagination remains 19 pages. The underlying figures and finite input records are unchanged.

All displayed indices, signs, multiplicities, canonical-jet terms, reflection/transition formulas, and conductor-three coefficients preserve the source formulas. The conditions on the genus-three tail bound are explicit, including an actual counting constant A versus normalized illustrative profiles with A=1. The fourth-log identity is retained as additional analytic input; divisor matching alone is not asserted to supply cubic reconstruction. The modulus theorem is not promoted to exact phase, a root-of-unity conclusion, or closure of U_Gamma=U_alg. Ordinary complex analysis and the open H12 equality are not newly Lean-formalized.

The companion JSON pins every final guide source/PDF hash and every final page raster/viewed-basis hash. The separate INDEPENDENT_VISUAL_RENDER_VERIFICATION.json in this audit directory records the independent 19-page render, exact 15-page preservation, and direct final-page review coverage. All 36 native PNG/PDF assets, both frozen generator/control files, and all five checked raw sources still match the final input-run hashes. No unresolved native-figure or guide-page defect remains.

This is a scoped visual/source audit; it is not a universal numerical certificate or a new proof of the open arithmetic comparison. The separate traditional transcription report covers only the named principal and reconstruction sections and their figure-only publication changes; it does not imply an independent audit of every external analytic theorem.
