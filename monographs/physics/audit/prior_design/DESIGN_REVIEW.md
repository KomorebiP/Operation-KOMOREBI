# Publication design review
## Komorebi Physics: Continuum, Geometry and Refinement

**Output:** `Komorebi_Physics.pdf` — 568 PDF pages, with an unnumbered cover, preliminary folios i–vii, and main folios 1–560.

### Design changes

The cover is now a typographic composition rather than a report cover with decorative wave motifs. White part openings replace full dark divider leaves. Navy headings, dark-teal section numbers, restrained copper rules, and muted running furniture distinguish the physics volume without competing with the mathematics on the page.

The main reading text is consistently set at 11 points, including the older backreaction and cosmology components previously set at 10 points. Genuine OpenType regular, italic, bold, and bold-italic faces are specified. Theorem presentation is restrained, captions are differentiated, long tables use controlled sizing, and long source paths may wrap. Mirrored gutters and outer folios provide a book-like spread. Front matter has Roman page labels; the mathematical body has Arabic folios. Running headers link back to the relevant contents page.

Five short cosmology part introductions are integrated into their chapter openings. Local page-break controls keep the last figure and its interpretation together, prevent isolated closing bullets or paragraphs, and consolidate one numerical benchmark into two aligned columns. Equations and numerical values in that benchmark are retained. The total page count rises from 558 to 568 because of the more legible legacy text and revised front matter, despite consolidation of short internal leaves.

### Completed document checks

- All 18 component documents built successfully with three TeX passes.
- Final logs contain no overfull boxes, undefined references, missing-glyph reports, or font-substitution warnings. Informational `unicode-math`/`mathtools` interoperability warnings remain; this is not a claim of completely warning-free logs.
- The final document contains 572 bookmarks, 835 internal link annotations, and 38 external URI annotations. All internal/bookmark destinations are valid. Source link annotations were compared to the mapped final pages; no discrepancy was found.
- The all-page text-bound scan found no extracted text outside the page media box, no empty-text pages, and no replacement-character pages. Bounds checks do not prove that every conceivable overlap is absent.
- PDFium rendered all 568 pages successfully. Representative page openings, proofs, tables, figures, and chapter endings were also inspected at higher resolution. Contact sheets are included for independent review. This is a document/layout review, not an independent reading of every mathematical argument.
- The final short-body-page heuristic reported no candidate pages after local flow repairs. Intentional chapter and part openings are excluded from that heuristic.

### Source-preservation checks

Comparison to the supplied predecessor source package found these sequences unchanged, in source-file order: **107 explicit proof environments**, **1,296 numbered display environments**, **642 unnumbered display environments**, and **113 explicit theorem/lemma/proposition/corollary/definition environments**. All **196 scientific figure assets** were byte-identical. The inherited formal archive, uncompiled generator module, and replay-status file were also byte-identical.

These are narrowly defined source-text and checksum checks. They do not establish correctness of the inherited proofs, completeness of every prose statement, successful Lean compilation, empirical validity, or bibliographic priority. The typography macro for bold mathematics was repaired to render the intended symbols rather than a missing-font fallback; scientific source expressions were not rewritten.

### Failures and repairs

1. A streaming container invocation was rejected before execution. Ordinary execution and a real logged subprocess were used instead.
2. An initial helper failed while extracting the old assembly specification. The reader was corrected to handle tuple-shaped targets and use the pristine predecessor script.
3. Name-based bold-font selection caused five intermediate XeLaTeX builds to fail in `xdvipdfmx`. Explicit installed OpenType files replaced the ambiguous font resolution. All 18 final builds then passed, without substitution warnings.
4. A tracked-text helper leaked character spacing into following ReportLab paragraphs, pushing preview text off the page. Local graphics-state isolation fixed the defect; final page-bound scans and visual checks passed.
5. A shared panel-style hook temporarily hid panel titles. The overriding hook was removed and the titles were verified in the rebuilt pages.
6. The first bookmark assembly duplicated source-main bookmarks in relocated appendices. Restricting bookmarks to each selected source-page subset removed the duplicates.
7. A long legacy chapter heading and one data-file path overran the enlarged text measure. Ragged-right chapter titles and a wrapping path command corrected them.
8. Sparse chapter tails were identified and repaired with local page controls, compact standard bibliography sizing, integrated introductions, and the aligned benchmark layout.

No unresolved final document-build or render failure was found. The logs retain earlier failed attempts rather than representing them as passes.

### Boundaries and delivery

The navy/teal/copper design is a publication choice, not an additional mathematical or physical claim. The book is not newly certified in Lean. It is not declared PDF/A or a tagged accessibility-conformant PDF, and it has not been preflighted to a particular commercial printer's trim/bleed specification. It is a searchable, linked reading PDF with vector source pages and a reproducible source build.

No font binaries are distributed. Fonts embedded as part of the PDFs support their rendering. Existing source rights and notices remain unchanged.

The exact page counts, destinations, hashes, font inventory, source comparisons, build results, and render results are in the adjacent machine-readable audit files.
