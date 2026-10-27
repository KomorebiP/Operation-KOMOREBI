# Final main-manuscript visual review

## Result

**PASS for visual release.** All 99 pages of the final main manuscript are covered by the complete baseline review and full-page review of every page changed in two layout passes. Both material figure/statement interruptions found during the review are resolved. No remaining material clipping, readability, blank-page, or figure-placement issue was found at the inspected scales.

This report concerns visual layout and reading flow. It does not add a fresh mathematical proof audit or formal-coverage claim.

## Final PDF binding

- File: `/workspace/scratch/9014da510e4f/paper3_release/publication/Paper_III_Final_v1.0.0.pdf`
- SHA-256: `fb5d7a81487ef1e37bb4aa8fed12bd4cce9b6d9b2df667429173ed8299e8db77`
- Size: **602,199 bytes**; **99 physical pages**.
- Immutable QA snapshot: `paper3_visual_qa/main_agent/post_repair_2/Paper_III_Final_repaired_snapshot.pdf`.
- Page convention: physical page 1 is the cover, physical 2–4 are roman i–iii, and physical page 5 begins printed page 1. Thereafter printed page = physical page − 4.

The final publication file and QA snapshot were checked against the same hash. The report preserves the earlier reviewed hashes and image manifests below; it does not silently apply an old inspection to a changed PDF.

## Exact visual coverage

| Revision / inspection | Coverage | Actually inspected | Result |
|---|---|---:|---|
| Original baseline: every contact sheet | Physical pages 1–99 | 25 contact-sheet images | All pages inspected; Figure 5 interruption found |
| Baseline: personal full-page review | Physical 6–24, 26–31, 35–39 | 30 page images at 120 dpi | Dense finite-core material, ledger, early diagrams and Section 17 inspected |
| Baseline: supplementary full-page review | Physical 40–79 | 40 page images at 144 dpi | All assigned mathematical pages and initial atlas plates inspected |
| Baseline: supplementary full-page review | Physical 80–98 | 19 page images at 120 dpi | Remaining atlas plates inspected |
| After Figure 5 repair | Every changed page: 4, 49, 51–70, 72–73, 78, 95–96 | 27 changed pages plus unchanged 50 and 71 as context: 29 unique images | Figure 5 fixed; reflow exposed Figure 6 interruption |
| After Figure 6 repair: final PDF | Every changed page: 70, 72, 73 | 3 page images at 120 dpi | Both findings closed; no new issue |

The baseline covered all 99 pages in contact sheets and 89 unique pages as full-page images. Because physical page 4 was additionally opened at full-page scale during the first repair, the review carried to the final PDF includes **90 unique physical pages at full-page scale**. Physical pages 1–3, 5, 25, 32–34, and 99 received contact-sheet review only and remained pixel-identical through both layout passes.

Across all three revisions, **146 unique image files were actually opened and inspected**. Some were independently inspected by both reviewers; the JSON records the reviewers without counting those files twice. It lists every inspected image, its page coverage, dimensions, dpi where applicable, and SHA-256. Rendering a file was not counted as inspecting it.

## Comparison evidence

All pages were rendered with Poppler at 120 dpi for each revision. The observed 120 dpi rendering commands completed with exit code 0. The comparison used exact RGB pixel differences with equal image dimensions, rather than PDF binary equality.

| Comparison | Reviewed PDF hashes | Changed pages | Pixel-identical pages |
|---|---|---:|---:|
| Baseline to Figure 5 repair | `847f242b…` → `e5de4c6e…` | 27 | 72 |
| Figure 5 repair to final Figure 6 repair | `e5de4c6e…` → `fb5d7a81…` | 3 | 96 |

Every changed page was inspected as a full-page image at original image detail. The 96 unchanged final pages inherit the previous revision's completed review through exact 120 dpi pixel equality. The JSON contains a per-page coverage record and the complete equivalence chain back to the last required visual inspection.

The complete historical hashes are:

- Baseline: `847f242b12d6c5ca0fabee33f08b5243fb08734f61ece60c1adf4199a2d7b266`, 602,088 bytes, 99 pages.
- After Figure 5 repair: `e5de4c6e348c5be4c8c4bc49dc15be7aeaee285c28b47e0145aa2fedecd834e1`, 602,047 bytes, 99 pages.
- Final after Figure 6 repair: `fb5d7a81487ef1e37bb4aa8fed12bd4cce9b6d9b2df667429173ed8299e8db77`, 602,199 bytes, 99 pages.

## Resolved findings

### VIS-MAIN-001 — Figure 5 inside Theorem 21.3

**Status: closed in the final PDF.** In the original baseline, Theorem 21.3 began on physical page 49 with “Suppose” and a commutative square, Figure 5 occupied physical page 50, and the same theorem sentence resumed on physical page 51. This was a material reading-flow defect.

The root agent inserted `\clearpage` after the Figure 5 environment and before the theorem labeled `thm:obstruction_naturality` in `manuscript/chapters/03_nonlinear_coordinates.tex`. The repaired page 49 now ends after complete Theorem 21.2 material; Figure 5 occupies page 50; and **all of Theorem 21.3 and its proof appear together on page 51**. Those repaired pages were inspected in the first layout pass and are pixel-identical in the final PDF.

### VIS-MAIN-002 — Reflow moved Figure 6 inside Theorem 27.8

**Status: closed in the final PDF.** The Figure 5 repair reflowed later text. In that intermediate PDF, Theorem 27.8 began at the foot of physical page 70, Figure 6 occupied physical page 71, and the same statement resumed on physical page 72 with its operator-norm qualification and error bound. This new issue was reported immediately before release approval.

The root agent inserted `\clearpage` after the Figure 6 environment and before `thm:sampled_transport_convergence` in `manuscript/chapters/04_correction_transport.tex`. In the final PDF, physical page 70 ends after the complete Theorem 27.7 proof and explanatory callout. Figure 6 occupies page 71. **All of Theorem 27.8, including its convergence statement and error bound, and its entire proof now appear together on page 72.** Page 73 has a clean direct continuation of the later standard fact's proof and the concluding section. All three changed pages were inspected.

Both corrections concern placement and readability. Neither finding was a mathematical gap, and this reviewer made no manuscript or publication PDF edits.

## Other results

No remaining visible text or formula clipping, overlap, missing-glyph boxes, or unreadable mathematical glyphs was found at the inspected scales. Formal declaration strings and ledger columns wrap within their allotted width. Dense displayed mathematics, including subscripts and superscripts, remains legible in full-page views.

No accidental blank page was found. Short section-boundary pages, dedicated figure pages, and the appendix introduction are intentional. Ordinary direct page continuations were not treated as defects; the two resolved issues each inserted an entire figure page inside a single statement.

All six main figures, the formal ledger, dense mathematical sections, and all 24 atlas plates received full-page review. Section 17's Figure 4 remains between complete preceding material and the following norm proposition, and those pages are unchanged in both later passes.

All atlas diagrams, matrices, tables, arrows, curves, labels, captions, and callouts remain contained and readable. First-pass changes on physical pages 78, 95, and 96 were confined to small page-locator digit regions. All atlas pages are pixel-identical between the first and final layout passes.

## Supplemental checks, provenance, and limits

The final PDF's geometry record contains all 99 pages. Every page contains extracted text, and no extracted text-block bounding box extends outside its page rectangle. These checks supplement the visual review; they do not substitute for looking at the pages.

The 120 dpi images are 1020 × 1320 pixels. Baseline supplementary pages 40–79 were additionally inspected at 144 dpi, 1224 × 1584 pixels. No runtime duration is asserted. The supplementary reviewer did not retain an exit-code observation for the 144 dpi render batch, so none is claimed.

All snapshots, image files, contact sheets, child reports, and comparison/geometry manifests are under `paper3_visual_qa/main_agent`. The baseline report is preserved as `baseline_review_main.md` and `.json`; supplementary baseline reports are `zoom_review_40_98.md` and `.json`. The first layout pass is retained under `post_repair`, including `personal_delta_review.json` and `zoom_delta_review.md`/`.json`. The final pass is retained under `post_repair_2`, including the final snapshot, comparison manifest, geometry, and personal review. The aggregate JSON records exact paths and hashes, and a relative-path mapping can preserve their identities when packaging.

The conclusion applies to the final SHA-256 above and the recorded inspection scales. Any later PDF revision requires a comparison against this reviewed final rendering and visual checking of changed pages.
