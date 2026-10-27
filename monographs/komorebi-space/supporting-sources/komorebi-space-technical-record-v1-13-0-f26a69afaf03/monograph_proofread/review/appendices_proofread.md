# Appendices and worked examples: final proofreading

Mode: edit mode, using the mathematical proofreading skill and checklist.

## Coverage

All seven assigned files were read in full, covering 626 original source lines:

- `source/chapters/06_boundaries.tex` — changed.
- `source/chapters/06_cases.tex` — changed.
- `source/chapters/07_concordance.tex` — changed after integrated PDF review.
- `source/chapters/08_references.tex` — no objective change needed.
- `source/chapters/09_workshop.tex` — changed.
- `source/chapters/10_hypothesis_atlas.tex` — changed.
- `source/chapters/11_written_extensions.tex` — no objective change needed.

## Changes

Seven local edits were made. No numbered theorem, proposition, example, section, proof, or formal source was added or removed. The existing mathematical results and their numerical values are unchanged.

1. `source/chapters/06_boundaries.tex`, original line 16. Clarify the three functor properties already named, including the parallel-arrow scope and the isomorphism in essential surjectivity. No theorem changes.

   Before: `Faithfulness asks whether distinct semantic arrows can become indistinguishable. Fullness asks whether every compatible comparison comes from a semantic one. Essential surjectivity asks whether every intended coherent datum is realized by an actual semantic object.`

   After: `Faithfulness asks whether distinct semantic arrows with the same source and target can become indistinguishable. Fullness asks whether every arrow between the images of two semantic objects comes from an arrow between those objects. Essential surjectivity asks whether every object of \(\mathcal K\) is isomorphic to the image of an actual semantic object.`

2. `source/chapters/06_cases.tex`, original line 171. The stated residual norm is a Euclidean sum of squares; the following square-root-of-two factor is unchanged.

   Before: `each isometric edge contributes its norm twice`

   After: `each isometric edge contributes its squared residual norm twice`

3. `source/chapters/09_workshop.tex`, original line 44. Repeat the exact definition already supplied in Section variable-exactification, allowing workshop 6 to be read directly.

   Before: `Compare the paths $(1,0,(n+1)^{-1})$ and $(1,H_n,(n+1)^{-1})$. Which hypotheses distinguish them?`

   After: `Compare the paths $(1,0,(n+1)^{-1})$ and $(1,H_n,(n+1)^{-1})$, where $H_n=\sum_{j=1}^{n}1/j$. Which hypotheses distinguish them?`

4. `source/chapters/09_workshop.tex`, original line 69. State explicitly the ambient metric used by the existing Gram matrix and objective calculation.

   Before: `Let $p(a)=a_1-2a_2$, $d(a)=a_1$, $r=1$, and $\alpha=1$. Compute the protected regularized correction`

   After: `In Euclidean $\R^2$, let $p(a)=a_1-2a_2$, $d(a)=a_1$, $r=1$, and $\alpha=1$. Compute the protected regularized correction`

5. `source/chapters/10_hypothesis_atlas.tex`, original line 11. Repeat the exact sequential inverse-system hypothesis of KS58 in its atlas entry; no stronger or new existence result is introduced.

   Before: `An infinite point from finite views & Nonempty finite fibers, or another proved lifting/compactness hypothesis.`

   After: `An infinite point from finite views & A sequential inverse system with nonempty finite fibers, or another proved lifting/compactness hypothesis.`

6. `source/chapters/10_hypothesis_atlas.tex`, original line 52. Use the actual title of the supplied companion guide.

   Before: `The companion evidence guide records these scopes`

   After: `The companion Lean guide records these scopes`

## Mathematical wording and additions

Five of the edits involve mathematical definitions, quantities, or explicit hypotheses and are recorded as such, even though no displayed formula was corrected:

- Faithfulness/fullness/essential-surjectivity wording: specify parallel arrows, images of the specified objects, and isomorphism. These are clarifications of the properties named in the preceding paragraph.
- Doubled orientations: “norm” becomes “squared residual norm.” The existing Euclidean sum-of-squares convention and the unchanged square-root-of-two factor uniquely force this wording.
- Workshop 6: repeat `H_n=\sum_{j=1}^{n}1/j`, the exact existing definition from the main text.
- Workshop 11: state the Euclidean metric already used in `G=5` and the objective values.
- Hypothesis atlas: explicitly identify the sequential inverse system required by the cited finite-fiber proposition.

No new result, substantive proof repair, proof shortening, or numerical claim was introduced.

## Validation

- All 79 local reference occurrences resolve in the monograph sources.
- The one citation in these assigned prose files has a matching bibliography key. Bibliography entries were checked for local syntax and consistency. External source support was not reverified.
- All seven files have properly nested named LaTeX environments.
- All 53 representative declaration names in the formal-verification appendix occur in the accompanying Lean sources. This is a source-navigation check, not a new compilation or independent proof of coverage.
- Formal totals and the thirteen-of-sixteen coverage statement match the existing edition verification record.
- Every changed sentence was reread in its surrounding paragraph.
- No full build was run during concurrent source edits. The integrated build and page review are pending under the root agent.

## Findings and limits

No unresolved proof-level defect was identified within this proofreading scope. This is conservative local consistency review, not an independent referee audit of every proof or a new Lean compilation.

No command failure occurred in this subtask. Source files are frozen for integration.

## Integrated PDF review follow-up

The initial PDF review found an isolated final line of Appendix C on physical page 150. The final paragraph of `07_concordance.tex` was trimmed to an equivalent three-sentence formulation, preserving its source-navigation and accepted-compilation statements. No mathematical token changed.

Before: `The full source also contains supporting definitions, lemmas, and examples beyond this table. The companion Lean guide describes its organization and the formal treatment of the principal analytic results. Verification records retain the exact source inventories and declaration types used for the accompanying accepted compilation.`

After: `The source contains further definitions, lemmas, and examples beyond this table. The Lean guide explains its organization and the formal treatment of the principal analytic results. Verification records retain the exact source inventories and declaration types from the accepted compilation.`

The source was reread and frozen again. The root will rebuild and request a page recheck.

A separate initial bibliography finding was a **false positive**: I misread entries [1] and [2] as running together. Reinspection of the exact same page-161 PNG at original detail confirms that they are correctly separated, with matching image SHA-256 `a28fdcf9159438f588d3d3207d2ad8cdf60eba6f3af366f68c12dbb43461af4e`. That finding is retracted. No bibliography source edit was made. The initial PDF review record is preserved unchanged, and its correction is recorded here and in `appendices_pdf_review_corrections.json`.
