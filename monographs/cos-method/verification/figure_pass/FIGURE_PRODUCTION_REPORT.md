# K-COS figure-production report

## Deliverable

The rebuilt monograph has **141 pages**, four parts, twelve chapters, and four appendices. It contains **50 independent vector graphics**: all 49 figures from the technical baseline have been rebuilt, and a directed-enclosure refinement figure has been added. Each graphic is supplied as a vector PDF, editable SVG, and PNG preview. The book itself contains no embedded raster images.

The baseline is `K_COS_Monograph_Revised_Package.zip`, the corrected monograph with the running example. This pass did not revert to any earlier manuscript or design branch.

## Production changes

A single Python/matplotlib figure system now governs typography, line weights, markers, legends, annotation spacing, and full-width placement. Plum identifies exact or primary objects, teal identifies represented or approximate quantities, ochre identifies bounds, and rust highlights failures. Categorical experiments use additional markers and explicit labels. Line styles, markers, and written decisions supplement color. Six representative graphics were also inspected in grayscale.

The new graphics include the operator pipeline, exact Gram assembly, projection geometry, phase frontiers, storage and scheduling models, range and residual bounds, centered packets, cosine inversion, arithmetic-width decomposition, accuracy refinement, and empirical controls. The visual atlas has been rebuilt in the same system. Main figure captions explain what is shown, its mathematical point, and its evidence level.

The new worked-example figure shows the two retained directed enclosures on spectrum (1,1,2,2) at q=40. Its 8,192-mode enclosure has a ratio width of about 2.461%, which fails the requested 2%. Its 16,384-mode enclosure has a width of about 1.373%, which passes. The displayed endpoints are reference-centered and rounded for plotting. The retained decimal records, not plotted pixels, govern the decisions.

## Data fidelity

The three original packet-experiment CSV files were recovered from the retained source ZIP. Their recovered bytes were compared with the archive members. No chart was traced from a raster image and no missing experimental vector was invented.

Recorded zeros remain zero. Symmetric-log axes are used when necessary rather than replacing zeros with arbitrary positive floors. Infinite Weyl widths are identified explicitly. The residual-width figure includes its small final values rather than clipping them out of view. The discrepancy overview includes both positive and signed control families, and the synthetic-LD plot includes the retained deeper copy-LD records. Timing models are labeled as models, not measurements.

The fixed-resolution width chart uses the corrected full-decimal endpoint record, not the obsolete binary64-subtraction widths. Two very-deep accuracy summaries are transcribed from the book as rounded values and identified as such in `illustrations/publication_data/README.md`. The rank-allocation and QR figures use the actual retained rank and discrepancy audits. Unavailable singular-value vectors are not reconstructed.

## Executed checks

| Check | Result |
| --- | --- |
| Figure regeneration | 50 graphics generated, with PDF/SVG/PNG outputs |
| Data-source correspondence | All recorded source hashes match |
| Packet table recovery | All three CSV files match their archived bytes |
| Canvas text bounds | Passed for all 50 figures |
| Finite line/scatter data bounds | Passed for 10,160 plotted coordinate pairs |
| Vector assets | 50 single-page PDFs, no embedded raster images |
| Engine and data preservation | 150 baseline files unchanged |
| Lean-project preservation | 31 baseline files unchanged |
| Mathematical source preservation | All 61 theorem-family environments and all 39 proof environments are literally unchanged |
| Baseline source labels | All 186 preserved; one new figure label |
| Navigation | 144 bookmarks and 156 links; no invalid internal destinations |
| PDF geometry | No empty text pages or words outside page bounds |
| Final LaTeX build | No unresolved references/citations, duplicate-label, missing-character, overfull-box, or underfull-box diagnostics |

All pages were rendered. Contact sheets for the changed figure pages were reviewed, with selected graphics and pages inspected at larger resolution. The atlas opening was shortened to keep its closing note and reading connection on the same page. The figure font and legend checks were supplemented by visual inspection; geometric checks alone do not prove that every design choice is optimal.

The illustration generator also executes finite assertions for declared integer block identities, phase zeros, residual completion, and selected bound comparisons. Their exact scope is recorded per figure in `figure_manifest.json`. Numerical comparisons in illustrative plots are not directed interval certificates.

## Source changes outside the plots

The theorem and proof environments were not edited. Figure paths and captions changed. The atlas payoff formula now uses its already-defined endpoint b consistently in place of the stray U. The atlas opening was tightened to avoid an orphaned closing note. The reproduction appendix now identifies the publication-figure generator and explicitly separates the retained engine replay from this figure pass. A complete text-source diff is included.

## Recovered issues during production

Initial generation attempts were interrupted during font-cache preparation or by execution limits. A math-text transpose command needed braced syntax. The first bounds check also flagged out-of-view tick labels that Matplotlib does not draw; those are now excluded from the canvas test. A reference equality line extended beyond the chosen axis range and was shortened to the visible domain without altering the data.

Rendered review exposed title/legend collisions, long axis labels, a clipped near-zero residual endpoint, and an atlas note stranded on the following page. Legend space is now measured before export, the affected labels are wrapped, the residual axis retains zero, and the atlas introduction has been reflowed. The final generation, build, and audits completed successfully. These issues and their fixes did not modify engine outputs or empirical input files.

## Limits

**The 60-test engine regression suite and the independent interval controls were not rerun in this figure-production pass.** Their earlier execution records remain in `verification/current_revision/` and are not presented as new results. The input files were preserved and checked, while the declared visual models were regenerated.

**Lean was not recompiled.** The 26-theorem, eight-definition formal companion and its existing compiler records are retained unchanged. This pass does not add formal coverage, establish end-to-end numerical correctness, or make a new performance claim.

Source hashes, data checks, and rendered-page inspection establish the stated production checks. They do not independently prove every mathematical assertion in the monograph.

## Reproduction

```text
python -m pip install -r requirements-illustrations.txt
python illustrations/production_figures.py
python build.py
python verification/figure_pass/audit_publication.py
python verify_manifest.py
```

Regeneration changes output bytes and therefore the delivered checksum manifest. Work on a copy to preserve the original package. Source fonts are referenced by name and embedded as permitted in PDF outputs; no font binaries are supplied.
