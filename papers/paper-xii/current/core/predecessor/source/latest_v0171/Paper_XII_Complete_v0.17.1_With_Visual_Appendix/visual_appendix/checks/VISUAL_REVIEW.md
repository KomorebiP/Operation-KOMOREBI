# Visual and editorial review

## Final files

- Appendix: 18 pages, V–1 to V–18.
- Combined edition: 54 pages, preserving the original 36 pages before the appendix.
- The appendix has no raster image objects. Its graphics and equations are vector content.
- All embedded fonts reported by `pdffonts` are embedded subsets; no standalone font files are distributed.

## Review performed

Every appendix page was rendered with Poppler `pdftoppm` at 140 dpi and inspected in
an all-page contact sheet. Mathematical graphics and dense pages were also examined
at page scale, including the point-count lattice, support geometry, nilpotent example,
complete node spectrum, stable-core image arrays, and finite/infinite carrier comparison.
Label spacing and a caption paragraph-boundary issue were corrected and re-rendered.
The final page-label/source-heading mapping is V–n = page n for every n from 1 to 18.

The final LaTeX build reports no overfull boxes, no underfull-box warnings, and no
unresolved references. Programmatic inspection found no text outside the checked
page-safe bounds and no empty/spill pages. These geometric checks supplement, rather
than replace, visual review.

Every page of the original manuscript was compared with its counterpart in the
combined PDF: exact extracted text and pixel output at 54 dpi match on all 36 pages.
The appendix's 18 pages also match after integration. Internal link targets are valid,
and separate manuscript/appendix bookmarks and page labels are present.

## Mathematical presentation safeguards

Coordinate drawings are explicitly labeled real closed-point shadows rather than
complete depictions of spectra. The local node's three-point specialization diagram
is an exact spectrum description, with specialization arrows distinguished from ring
maps. Nilpotent thickness is explained using quotient algebras and test rings, not
arbitrary line thickness. The packet example separates the algebra, supplied module,
generalized eigenspace, ordinary eigenspace, and scalar fiber. Infinite examples have
explicit all-level arguments rather than claims extrapolated from finite arrays.

The appendix does not alter the formal theorem ledger or verify the source Lean
release again. Exact illustrative-example checks are recorded separately.
