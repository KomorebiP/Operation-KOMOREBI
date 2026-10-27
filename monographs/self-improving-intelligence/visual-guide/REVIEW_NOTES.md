# Visual guide review and validation

**Self-Improving Intelligence — A Visual Guide**  
**Komorebi P. · Operation Komorebi · Guide v1.0.0 · 8 October 2026**

## Scope

This is a new, 36-page visual companion to the unchanged 60-page first-edition
manuscript. It follows the same finite diagnostic example through improvements
to its controller, compiler, pruning rule, and acquisition representation. It
also explains model uncertainty, preserved evidence, repair scope, certificate
invalidation, resource prices, and the limits of recursive continuation.

All diagrams were drawn programmatically as vector geometry. The PDF contains
no raster illustrations. It has 36 bookmarks, eight clickable reading-route
links, and page-level source references. The source package includes 36 separate
SVG plates and three PNG previews. Fonts are embedded in the PDF; standalone
font files are not distributed.

## Source review and preservation

The manuscript and its review notes were read through Files. The original source
ZIP was extracted for its reference indexes and exact JSON receipts. Its supplied
integrity verifier passed for all 325 archived files. The original manuscript and
source ZIP were not edited. The guide's source PDF copy is byte-identical to the
original. Selected source JSON files are retained unchanged and pinned by hash.

Source references point to printed manuscript page numbers. The local finite
examples illustrate existing arguments, not new priority claims. The reference
work already identifies its standard mathematical foundations. This companion
adds no new literature claims and performs no new external literature review.

## Mathematical and explanatory checks

`code/check_guide.py` passed **12 focused groups and 2,978 checks**. The domains
and counts appear in `validation/guide_checks.json`. They cover the canonical
bit-query policy on all eight cells, its leaf ordering and highlighted cell-five
path, repair-aligned partitions, the max/sum storage recurrence, the four possible
sensor/model pairs, count-prefix completion at capacities 1 through 8, the
three synthesis counterexamples, selected signed-integer identities, paired
repair weights, price-specific cost changes, all 16 four-score hindsight paths,
and partial sums of diminishing positive gains.

The same script checks the numerical transcriptions against the unchanged
source records for shortcut compilation, streaming, equation admission,
quotient size, reacquisition, and certificate replacement. This is a check of
**what the source records say**, not a new execution of those source compilers.
The complete original 336,867-assertion suite was not rerun.

The highlighted eight-cell route is explicitly the canonical all-coordinate
policy. The actual source compiler's cell-five trace uses an equality query at
its last two-case branch. The guide does not misidentify those as the same
literal tree. The quotient illustration likewise labels its expression order
as schematic rather than claiming the pictured examples occupy those precise
positions in the original grammar.

The certificate diagram retains the separate arithmetic/acquisition and
repair/controller branches. A valid capacity expression is not substituted for
a repair-weight certificate. The resource plate preserves negative signs and
the distinction between semantic validity and a favorable cost assessment.

## Actual failures and corrections

1. The first PDF build stopped at the page-three layout guard: its explanatory
   note needed 29 points of body height but had only 25.48 available. The note
   panel was enlarged and moved upward. The body font was not reduced.
2. Render inspection exposed missing minus signs in the serif numeric display.
   The text layout held the correct negative numbers, but the selected display
   font lacked the minus glyph. The renderer was changed to use the mathematical
   face for unsupported characters while retaining the requested face elsewhere.
3. The first focused preflight subsequently failed on a missing XOR glyph in
   page-eleven body text. The same fallback was extended to formatted paragraphs.
   The final PDF is checked for null/replacement characters, and the negative
   values on page 28 must also extract with their actual minus signs.
4. An unused, unembedded default Helvetica resource was removed by explicitly
   setting the canvas's initial face. All six font resources in the final guide
   are embedded subsets.
5. The bit-query subset legend was added, and the repeated-rejection path was
   routed outside its boxes. These clarify the illustrated semantics and avoid
   interpreting line crossings as extra dependencies.

No local mathematical example or source-number transcription check failed.
The layout and glyph failures above were real document failures and are not
reclassified as mathematical successes. The final checks passed only after
regenerating the PDF.

## Visual and mechanical review

All 36 pages were rendered with Poppler and inspected in contact sheets.
Selected full pages were additionally rendered with PyMuPDF and inspected,
including the cover, both diagnostic trees, the unknown sensor, the missing
capacity feature, the quotient, the dependency graph, signed costs, sequential
evidence, and the semantic transport square. The final formatting revision
removed only the unused font resource; its Poppler images were compared with
the inspected rendering.

Mechanical checks found no out-of-page words, overlapping word boxes above the
stated detection threshold, null/replacement glyphs, or missing source footers.
They do not prove every diagram is conceptually correct. The selected full-page
and whole-document visual inspections provide a separate presentation check.

A fresh source copy was rebuilt and checked. Its page-by-page extracted PDF text,
PDF bytes, and mathematical check output were compared with the delivered guide.
The actual result appears in `validation/fresh_rebuild.json`.

## Limits

The checker and illustrations are authored within the same project. This is not
independent peer review, a Lean build, a complete re-proof of the manuscript, or
an empirical demonstration of general intelligence. Font substitution and
cross-platform byte identity are not certified. PDF/A and tagged accessibility
were not certified. SVG text is outlined for portable display; editable wording
remains in the Python source.

The final snapshot checksum inventory verifies the included files, not their
truth or independent origin. Verify it before rebuilding outputs whose receipts
include fresh execution times.
