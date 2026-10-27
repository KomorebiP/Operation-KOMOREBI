# Block05 failures, repairs and limitations

## Failures actually observed and repaired

1. The first figure-rendering run stopped on a mathtext `\pmod` command unsupported by the renderer. It was replaced by an explicit supported roman `mod` expression. All 32 figures subsequently rendered.
2. The first figure review found top legends and some axis labels too close to the bounds, inconsistent per-point marker colors, and cramped text in several diagram boxes. Margins were enlarged, semantic series were grouped consistently, and box labels were reflowed. The complete figures and PDF were reviewed again.
3. Full-page review found three headings breaking words at a line end. Those headings were shortened without changing their mathematical scope. Final pages 16, 21, 24 and both concordance pages were inspected at 150 dpi. All other pages retained their rendered appearance.
4. The first publication checker incorrectly treated 37 valid named internal destinations as unsupported links. It failed rather than passing them unchecked. The checker now resolves each name through the actual PDF destination tree and validates the page. The PDF links themselves did not need replacement. The failed initial receipt is retained.

Font subsetting emitted low-timestamp diagnostics for installed fonts. They did not stop figure generation. No font files are shipped. The final LaTeX log has no warning/overfull/underfull/missing-character diagnostics; this narrower statement does not claim every tool's stderr was empty.

## Reproducibility

The final isolated source rebuild passed strict atlas PDF byte identity, all 96 figure-export byte comparisons, exact page text, and 100-dpi page pixels. This is a result for the checked environment, not a universal build guarantee or a revision of older blocks' recorded byte-difference failures.

## Checks not performed

No fresh Lean/Lake compilation, direct arithmetic matrix-constructor replay, seven additional historical B03 arithmetic executions, new classical-source audit or external peer review occurred. The four named finite suites were run. Their examples and negative controls do not establish general arithmetic realization.

The complete B02 editable archive and terminal v0.45 receipt remain unrecovered. This block did not run a new search for either. The prior Henniart–Lemaire primary-PDF audit limit remains inherited. The original 109/51/234-page core readers were neither modified nor newly signed off.

## Mathematical boundaries

General realization, same-candidate H5, corrected-character occurrence in the same continuation113 candidate, and an independently required actual native marking/phase certificate remain separate obligations. The six native square bits and section/phase fields remain null in the atlas data. Positive transported-marking results are not weakened by importing the stronger independent native requirement.
