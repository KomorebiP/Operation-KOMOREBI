# Main manuscript visual release review

## Result

**All 99 pages of the frozen main PDF were visually reviewed. One material layout repair requires a post-build visual check:** Figure 5 interrupts the statement of Theorem 21.3. No second material layout issue was found.

This is a visual review, not a fresh mathematical proof or formal-coverage audit. The input binding below is historical: the publication pathname may now contain the root agent's rebuilt PDF. The preserved rendered images and their hashes identify what was actually inspected.

## Frozen input

- File: `/workspace/scratch/9014da510e4f/paper3_release/publication/Paper_III_Final_v1.0.0.pdf`
- SHA-256: `847f242b12d6c5ca0fabee33f08b5243fb08734f61ece60c1adf4199a2d7b266`
- Size: 602,088 bytes; 99 physical pages.
- Page convention: physical page 1 is the cover, physical 2–4 are roman i–iii, and physical page 5 begins printed page 1. Thereafter printed page = physical page − 4.

## Actual visual coverage

| Inspection | Reviewer | Physical pages | Count | Scale |
|---|---|---|---:|---|
| Every contact sheet | `/root/expanded_audit` | 1–99 | 99 pages in 25 images | From 120 dpi renders, four pages per sheet except final three |
| Full-page images | `/root/expanded_audit` | 6–24, 26–31, 35–39 | 30 | 120 dpi; original image detail |
| Full-page images | `/root/expanded_audit/main_math_zoom` | 40–79 | 40 | 144 dpi; original image detail |
| Full-page images | `/root/expanded_audit/main_math_zoom` | 80–98 | 19 | 120 dpi; original image detail |

The union is **all 99 pages at contact-sheet scale, with 89 unique pages additionally inspected as full-page images**. Pages 1–5, 25, 32–34, and 99 received contact-sheet review only. All six main figures, the formal ledger, dense mathematical sections, and all 24 atlas plates received full-page review. The supplementary reviewer completed exactly the assigned range 40–98.

The machine-readable companion `visual_review_main.json` lists every one of the **114 actually inspected image files**, with its reviewer, physical page coverage, dimensions, and SHA-256. Rendering a page without opening it was not counted as full-page inspection.

## VIS-MAIN-001 — Figure 5 interrupts Theorem 21.3

**Severity:** material reading-flow defect. **Location:** physical pages 49–51, printed pages 45–47.

Theorem 21.3, “Naturality of obstruction classes,” begins near the bottom of physical page 49 with “Suppose” and a commutative square. Physical page 50 contains the full-page Figure 5, “Correctable defect and cokernel residual.” The theorem resumes at the top of physical page 51 with “is a commuting square. Then”. An entire figure page therefore interrupts one mathematical statement and sentence.

Evidence:

- `paper3_visual_qa/main_agent/contact_sheets/contact_49_52.png`
- `paper3_visual_qa/main_agent/zoom_pages/page-49.png`
- `paper3_visual_qa/main_agent/zoom_pages/page-50.png`
- `paper3_visual_qa/main_agent/zoom_pages/page-51.png`

**Minimal repair:** flush Figure 5 before the theorem begins, by inserting `\clearpage` immediately after that figure environment and before the theorem labeled `thm:obstruction_naturality` in `manuscript/chapters/03_nonlinear_coordinates.tex` (baseline source around lines 943–950). The root agent owns the correction and final rebuild. This reviewer made no manuscript or PDF edits.

This finding concerns presentation; it does not identify a mathematical gap. The repair must be checked on the rebuilt PDF before this visual issue is marked closed.

## Other observations

No additional visible text or formula clipping, overlap, missing-glyph boxes, or unreadable mathematical glyphs was found at the inspected scales. The formal declaration strings and ledger columns wrap within their allotted width. Mathematical displays, including dense subscripts and superscripts, remain legible in full-page views.

No accidental blank page was found. Short pages at section boundaries, dedicated figure pages, and the appendix introduction are intentional. Direct continuations of theorem statements or proofs onto the immediately following page were not treated as defects.

Section 17's Figure 4 on physical page 38 now sits between complete material on physical page 37 and the norm proposition beginning on physical page 39. Figure 6 on physical page 71 follows the complete Theorem 27.8 proof and precedes Corollary 27.9. Neither creates the interruption observed at Figure 5.

All atlas plates, physical pages 75–98, received full-page review. Their diagrams, matrices, tables, curves, arrows, captions, and explanatory callouts are contained and readable.

## Supplemental checks and limits

Poppler rendered all 99 baseline pages at 120 dpi; the observed command completed with exit code 0. These renders are 1020 × 1320 pixels. The supplementary 144 dpi images are 1224 × 1584 pixels. No runtime duration is asserted.

The recorded `paper3_visual_qa/main_agent/pdf_geometry.json` contains a page count and text geometry for the same input hash. All 99 pages contain extracted text, and none has an extracted text-block bounding box outside the page rectangle. These are supporting checks, not substitutes for looking at the pages.

The report's coverage claims apply to the frozen input and the listed rendered images. A later PDF with a different hash requires a rendering comparison and visual checking of affected pages. The post-repair review is pending.

The supplementary reviewer's detailed historical report and 59-image manifest are `paper3_visual_qa/main_agent/zoom_review_40_98.md` and `.json`. Its input hash, assigned page list, and all image hashes were checked against the main review record.
