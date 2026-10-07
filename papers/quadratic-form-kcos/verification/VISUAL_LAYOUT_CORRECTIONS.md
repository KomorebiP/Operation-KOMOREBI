# Visual layout corrections

**Komorebi P. · October 7, 2026**

This revision corrects figure display and typography in all three companions. The earlier contact-sheet review missed collisions inside plots and diagrams. Page-bound checks alone did not detect those defects. The revised figures were inspected individually at native resolution, and the final PDF pages were inspected at 150 dpi.

## Corrected reading set

| Companion | Final pages | Principal corrections |
|---|---:|---|
| Traditional paper | 85 | 24 revised figure displays; external notes and legends; separated metrics; visible coincident curves; clearer diagrams and contents numbering; portable Markdown captions |
| Visual guide | 18 | Visible Gram-addition operators; panel and colorbar spacing; contained labels and box borders; legends outside curves; uncropped curves; larger illustrations; COS equation spacing |
| Lean guide | 7 | Separation between stacked summation definitions; clearer contents spacing; complete declaration table; remaining obligations together on one page |

The traditional paper retains seven untouched original figure displays. All original figure bytes remain in the inherited engine, the unchanged packet figures, or the original source archives. The corrected displays are distinguished from their originals by the figure-layout records. The editable Markdown files retain their sibling PNG assets. The traditional exporter now converts canonical TeX captions to ordinary Markdown math instead of leaving 17 viewer-dependent HTML math spans.

## Data and mathematical content

The original engine, source archives and Lean sources are unchanged. The root preservation check covers 190 protected files. It also compares the traditional theorem/proof text and all guide formulas, ignoring only explicit layout spacing. The traditional author separately verifies all 36 proof environments, 61 statement/remark/algorithm environments and 342 display-math blocks. Visual finite-control values match the previous edition exactly. Independent chart checks compare 197 early and 80 late plotted coordinates with the archived recipes and CSV fields.

Three historical plots could not be regenerated as complete native curves because their original singular-value or eigenvalue vectors were unavailable. Moving their old raster labels exposed pixels that the original opaque text had already overwritten. The publication replaces those displays with clean, explicitly described summaries:

- Phase-local rank: the recorded six-phase ranks and unused uniform basis widths.
- QR core: the exact identity and recorded singular-spectrum discrepancy metrics.
- Spectral packets: the formal center/moment definitions and the original rounded center and second-moment labels.

No hidden singular values or eigenvalues were inferred. The historical PNGs are retained. The replacement captions and provenance state this limitation. A category-label mismatch introduced during relayout was caught independently: the partition identifier is `fine_64`, even though that experiment has 32 blocks. The final label is Fine64, with the mapping documented.

The finite algebraic Lean scope and the original numerical verification scope remain the same. This layout revision does not add probability formalization, rerun the historical experiments, or strengthen the interval-library trust claim.

## Verification evidence

All 48 figure displays were inspected individually at native resolution. Independent page review covers the entire 85-page traditional paper, all 18 visual-guide pages and all seven Lean-guide pages. The final contents-spacing adjustment was checked separately, with raster comparisons tying unchanged pages to the already inspected revision. Structural PDF preflights found no page-bound overflow or replacement glyphs. Final TeX compilation logs are clean.

Evidence is recorded in:

- `publication/VISUAL_FIX_INDEPENDENT_REVIEW.md`, the independent figure and guide review.
- `publication/`, the independent traditional page-range reviews and raster comparisons.
- `LAYOUT_CONTENT_PRESERVATION.json`, the root content check.
- `../traditional/FIGURE_LAYOUT_REPORT.md`, the derivative methods and source limitations.
- `../traditional/FIGURE_RELAYOUT_EARLY.json` and `FIGURE_RELAYOUT_LATE.json`, input hashes and plotted arrays.
- `../traditional/MARKDOWN_CAPTION_EXPORT.json`, canonical caption conversion and asset checks.
- `../visual/validation/VISUAL_REPAIR_REPORT.json` and `../lean/verification/DISPLAY_REPAIR_AUDIT.json`, companion-specific repairs.

An initial formula comparison failed because its parser mistook the second backslash in a row-spacing command for a display-math delimiter. The corrected parser normalizes layout spacing and requires an unescaped delimiter. The comparison then passed without changing any formulas.

## Previous archive failure

The previous saved source ZIP failed to open: it was 1,520,606 bytes shorter than the successful packaging output and lacked its closing ZIP index. The cause of that discrepancy was not established. Its complete local records preserved the three PDF payloads and the seven baseline source/control files needed for this audit. Those records were recovered and checked against CRC32, baseline byte counts and SHA-256 hashes; the three PDF payloads parsed correctly.

This revision rebuilds the ZIP through a temporary file, verifies its CRCs, unique member names and every source-manifest hash, and replaces the destination only after those checks pass. The saved download is checked again before delivery. The recovered pre-layout sources and their original manifest are retained under `pre_layout_sources/`; the damaged ZIP is not included in the replacement bundle.
